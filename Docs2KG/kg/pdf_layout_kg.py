import json
from pathlib import Path
from typing import Optional
from uuid import uuid4

import pandas as pd
from sentence_transformers import SentenceTransformer

from Docs2KG.kg.constants import HTML_TAGS
from Docs2KG.utils.empty_check import empty_check
from Docs2KG.utils.get_logger import get_logger
from Docs2KG.utils.rect import BlockFinder

logger = get_logger(__name__)


class PDFLayoutKG:
    """
    Layout Knowledge Graph

    This is for one pdf file


    What we will link in the layout knowledge graph:

    - Document KG
        - Input is the Markdown JSON file
        - The context order will be preserved within the Tree
    - Link Image to Page
    - Link Table to Page
    - Link Image to Context (Find Nearby Context, then Map back to the Tree)
    - Link Table to Context (Same, Find Caption, Nearby Context)
    """

    def __init__(
        self,
        folder_path: Path,
        input_format: str = "pdf_exported",
    ):
        """
        Initialize the class with the pdf file


        Args:
            folder_path (Path): The path to the pdf file

        """
        self.folder_path = folder_path
        self.kg_folder = self.folder_path / "kg"
        if not self.kg_folder.exists():
            self.kg_folder.mkdir(parents=True, exist_ok=True)
        self.kg_json = {}
        self.metadata = json.load((self.folder_path / "metadata.json").open())
        self.sentence_transformer = SentenceTransformer("all-MiniLM-L6-v2")
        self.input_format = input_format

    def create_kg(self):
        """
        Create the layout knowledge graph
        """
        self.document_kg()
        if self.input_format == "pdf_exported":
            self.link_image_to_page()
            self.link_table_to_page()
            self.link_image_to_context()
            self.link_table_to_context()
        if self.input_format == "pdf_scanned":
            # add page image
            self.link_page_image_to_page()

    def document_kg(self):
        """
        Construct the layout knowledge graph skeleton first

        We will require the md.json.csv file with the following columns:

        - layout_json
        """
        # 1. add the document node

        self.kg_json = {
            "node_type": "document",
            "uuid": str(uuid4()),
            "node_properties": self.metadata,
            "children": [],
        }

        # 2. add page nodes
        pages_json = []
        text_folder = self.folder_path / "texts"
        md_json_csv = text_folder / "md.json.csv"
        texts_json_df = pd.read_csv(md_json_csv)
        columns = texts_json_df.columns.tolist()
        logger.debug(f"Columns: {columns}")
        # we will focus on the layout json

        for index, row in texts_json_df.iterrows():
            logger.info(f"Processing page_index {index}")
            logger.debug(row["layout_json"])
            try:
                layout_json = json.loads(row["layout_json"])
                # recursively decompose the layout json and add to proper level children

                page_json = {
                    "node_type": "page",
                    "uuid": str(uuid4()),
                    "node_properties": {
                        "page_number": row["page_number"],
                        "page_text": row["text"],
                    },
                    "children": [self.recursive_layout_json(layout_json)],
                }
                pages_json.append(page_json)
            except Exception as e:
                logger.error(f"Error in row {index}: {e}")
                logger.error(row["layout_json"])
                logger.exception(e)
                # if this is an unhandled error
                # we should still keep all data for this page, so we will construct a page with everything we have
                page_json = {
                    "node_type": "page",
                    "uuid": str(uuid4()),
                    "node_properties": {
                        "page_number": row["page_number"],
                        "page_text": row["text"],
                    },
                    "children": [],
                }
                pages_json.append(page_json)

        self.kg_json["children"] = pages_json
        self.export_kg()

    def link_image_to_page(self):
        """
        Loop the image, assign it under the proper page
        If the page not exist, then add a page node
        """
        block_images = self.folder_path / "images" / "blocks_images.csv"
        if empty_check(block_images):
            return
        images_df = pd.read_csv(self.folder_path / "images" / "blocks_images.csv")
        for index, row in images_df.iterrows():
            page_number = row["page_number"]
            page_node = self.get_page_node(page_number)
            if not page_node:
                logger.info(f"Page {page_number} not found, adding a new page node")
                page_node = {
                    "node_type": "page",
                    "uuid": str(uuid4()),
                    "node_properties": {
                        "page_number": page_number,
                        "page_text": "",
                    },
                    "children": [],
                }
                self.kg_json["children"].append(page_node)
            image_node = {
                "node_type": "image",
                "uuid": str(uuid4()),
                "node_properties": {
                    "image_path": row["image_path"],
                    "image_block_number": row["block_number"],
                    "bbox": row["bbox"],
                },
                "children": [],
            }

            page_node["children"].append(image_node)

        self.export_kg()

    def link_page_image_to_page(self):
        page_images_file = self.folder_path / "images" / "page_images.csv"
        page_images_df = pd.read_csv(page_images_file)
        for index, row in page_images_df.iterrows():
            page_number = row["page_number"]
            page_node = self.get_page_node(page_number)
            if not page_node:
                logger.info(f"Page {page_number} not found, adding a new page node")
                page_node = {
                    "node_type": "page",
                    "uuid": str(uuid4()),
                    "node_properties": {
                        "page_number": page_number,
                        "page_text": "",
                    },
                    "children": [],
                }
                self.kg_json["children"].append(page_node)
            image_node = {
                "node_type": "page_image",
                "uuid": str(uuid4()),
                "node_properties": {
                    "image_path": row["image_path"],
                },
                "children": [],
            }
            page_node["children"].append(image_node)

    def link_table_to_page(self):
        """
        Link the table file to proper page.

        Link to proper position in the page will be in function

        `link_table_to_context`

        """
        tables = self.folder_path / "tables" / "tables.csv"
        if empty_check(tables):
            return
        table_df = pd.read_csv(self.folder_path / "tables" / "tables.csv")
        for index, row in table_df.iterrows():
            logger.info(f"Processing table {index}")
            page_node = self.get_page_node(row["page_index"])
            page_node["children"].append(
                {
                    "node_type": "table_csv",
                    "uuid": str(uuid4()),
                    "node_properties": {
                        "table_path": row["file_path"],
                        "table_index": row["table_index"],
                        "bbox": row["bbox"],
                    },
                }
            )

        self.export_kg()

    def link_image_to_context(self):
        """
        Construct the image knowledge graph
        """
        block_images = self.folder_path / "images" / "blocks_images.csv"
        if empty_check(block_images):
            return
        images_df = pd.read_csv(self.folder_path / "images" / "blocks_images.csv")
        text_block_df = pd.read_csv(self.folder_path / "texts" / "blocks_texts.csv")
        logger.debug(text_block_df.columns.tolist())
        for index, row in images_df.iterrows():
            page_number = row["page_number"]

            logger.info(f"Processing image {index} in page {page_number}")
            page_node = self.get_page_node(page_number)
            # get the text blocks that are in the same page
            text_blocks = text_block_df[
                text_block_df["page_number"] == page_number
            ].copy(deep=True)
            # clean the text_block without text after text clean all space
            text_blocks = text_blocks[
                text_blocks["text"].str.strip() != ""
            ].reset_index()
            image_bbox = row["bbox"]
            logger.debug(f"Image bbox: {image_bbox}")
            text_blocks_bbox = text_blocks["bbox"].tolist()
            nearby_text_blocks = BlockFinder.find_closest_blocks(
                image_bbox, text_blocks_bbox
            )
            nearby_info = []
            nearby_info_dict = {}
            for key, value in nearby_text_blocks.items():
                if value is not None:
                    text_block = text_blocks.loc[value]
                    logger.debug(text_block)
                    nearby_info.append(
                        {
                            "node_type": "text_block",
                            "uuid": str(uuid4()),
                            "node_properties": {
                                "text_block_bbox": text_block["bbox"],
                                "content": text_block["text"],
                                "position": key,
                                "text_block_number": int(text_block["block_number"]),
                            },
                            "children": [],
                        }
                    )
                    nearby_info_dict[key] = {"content": text_block["text"], "uuids": []}
            """
            We also need to loop the nodes within this page
            if the text block is highly similar to a content node, then we can link them together

            How we solve this problem?

            Recursively loop the children of the page node, if the text block is highly similar to the content
            then we can link them together

            So the function input should be the page_node dict, and the nearby_info_dict
            Output should be the updated nearby_info_dict with the linked uuid
            """
            nearby_info_dict = self.link_image_to_tree_node(page_node, nearby_info_dict)
            logger.info(nearby_info_dict)

            for item in nearby_info:
                key = item["node_properties"]["position"]
                item["linkage"] = nearby_info_dict[key]["uuids"]

            """
            find the image node
            add the nearby_info to the children
            the image node will have the image_block_number to identify it
            """
            for child in page_node["children"]:
                if (
                    child["node_type"] == "image"
                    and child["node_properties"]["image_block_number"]
                    == row["block_number"]
                ):
                    child["children"] = nearby_info
                    break

        self.export_kg()

    def link_table_to_context(self):
        """
        Link the table to the context

        We have two ways to make it work

        1. Loop the table, and for tree leaf within the page node, if it is tagged as table, then link them together
        2. We have bbox of the table, so we can find the nearby text block, and link them together

        """
        tables = self.folder_path / "tables" / "tables.csv"
        if empty_check(tables):
            return
        table_df = pd.read_csv(self.folder_path / "tables" / "tables.csv")
        text_block_df = pd.read_csv(self.folder_path / "texts" / "blocks_texts.csv")
        for index, row in table_df.iterrows():
            page_number = row["page_index"]
            page_node = self.get_page_node(page_number)
            table_bbox = row["bbox"]
            text_blocks = text_block_df[
                text_block_df["page_number"] == page_number
            ].copy(deep=True)
            text_blocks = text_blocks[
                text_blocks["text"].str.strip() != ""
            ].reset_index()
            text_blocks_bbox = text_blocks["bbox"].tolist()
            nearby_text_blocks = BlockFinder.find_closest_blocks(
                table_bbox, text_blocks_bbox
            )
            nearby_info = []
            nearby_info_dict = {}
            for key, value in nearby_text_blocks.items():
                if value is not None:
                    text_block = text_blocks.loc[value]
                    nearby_info.append(
                        {
                            "node_type": "text_block",
                            "uuid": str(uuid4()),
                            "node_properties": {
                                "text_block_bbox": text_block["bbox"],
                                "content": text_block["text"],
                                "position": key,
                                "text_block_number": int(text_block["block_number"]),
                            },
                            "children": [],
                        }
                    )
                    nearby_info_dict[key] = {"content": text_block["text"], "uuids": []}
            nearby_info_dict = self.link_image_to_tree_node(page_node, nearby_info_dict)
            for item in nearby_info:
                key = item["node_properties"]["position"]
                item["linkage"] = nearby_info_dict[key]["uuids"]

            # the second matching method, loop the tree node of the page
            table_nodes = self.get_specific_tag_nodes(page_node, "table")
            page_tree_table_node = None
            # matched table nodes
            table_index = row["table_index"]
            if len(table_nodes) >= table_index:
                page_tree_table_node = table_nodes[table_index - 1]

            # give table node a linkage to the table_node
            for child in page_node["children"]:
                if (
                    child["node_type"] == "table_csv"
                    and child["node_properties"]["table_index"] == row["table_index"]
                ):
                    child["children"] = nearby_info
                    if page_tree_table_node:
                        # add the linkage from table_csv to table_tree_node
                        child["linkage"] = [page_tree_table_node["uuid"]]
                    break

        self.export_kg()

    def export_kg(self) -> None:
        """
        Export the knowledge graph to json file
        """
        with open(self.kg_folder / "layout_kg.json", "w") as f:
            json.dump(self.kg_json, f, indent=2)

    def load_kg(self):
        """
        Load the knowledge graph from JSON
        """
        with open(self.kg_folder / "layout_kg.json", "r") as f:
            self.kg_json = json.load(f)

    def get_page_node(self, page_number: int) -> Optional[dict]:
        """
        Get the page node

        Args:
            page_number (int): The page number

        Returns:
            page_node (dict): The page node
        """
        for page in self.kg_json["children"]:
            if str(page["node_properties"]["page_number"]) == str(page_number):
                return page
        logger.error(f"Page {page_number} not found")
        return None

    def get_specific_tag_nodes(self, tree_json: dict, tag: str) -> list:
        """
        Get the specific tag nodes from the page node

        Args:
            tree_json (dict): The tree_json
            tag (str): The tag to find

        Returns:
            list: The list of nodes with the specific tag
        """
        nodes = []
        if "children" not in tree_json:
            return nodes
        for child in tree_json["children"]:
            if child["node_type"] == tag:
                nodes.append(child)
            nodes.extend(self.get_specific_tag_nodes(child, tag))
        return nodes

    @classmethod
    def recursive_layout_json(cls, layout_json: dict) -> dict:
        """
        Recursively processes layout JSON to construct a tree structure, annotating each node with
        a unique identifier and handling specific HTML structures like tables.

        Args:
            layout_json (dict): The layout JSON object to process.

        Returns:
            dict: A tree-like JSON object with added metadata.
        """
        try:
            return cls._process_node(layout_json)
        except Exception as e:
            logger.exception("Failed to process layout JSON")
            return cls._error_node(layout_json, str(e))

    @classmethod
    def _process_node(cls, node: dict) -> dict:
        """
        Process a single node in the layout JSON.

        Args:
            node (dict): The node to process.

        Returns:
            dict: The processed node.
        """
        tag = node.get("tag")
        if tag in HTML_TAGS:
            return cls._create_tree_node(tag, node)

        # If 'tag' is missing, attempt to find a valid HTML tag in the keys
        for key in node:
            if key.strip() in HTML_TAGS:
                return cls._create_tree_node(key, node)

        # If no valid tag is found, handle as an untagged node
        return cls._untagged_node(node)

    @classmethod
    def _create_tree_node(cls, tag: str, node: dict) -> dict:
        """
        Create a tree node for the JSON structure.

        Args:
            tag (str): The HTML tag of the node.
            node (dict): The original node data.

        Returns:
            dict: A structured tree node.
        """
        node_uuid = str(uuid4())
        node_properties = {
            "content": node.get("content", ""),
            "text": json.dumps(node) if tag == "table" else "",
            "records": node.get("children", []) if tag == "table" else [],
        }
        children = [cls._process_node(child) for child in node.get("children", [])]

        return {
            "node_type": tag,
            "uuid": node_uuid,
            "node_properties": node_properties,
            "children": children,
        }

    @classmethod
    def _untagged_node(cls, node: dict) -> dict:
        """
        Handles nodes without a recognized HTML tag.

        Args:
            node (dict): The node to handle.

        Returns:
            dict: A default structured node indicating an untagged element.
        """
        return {
            "node_type": "untagged",
            "uuid": str(uuid4()),
            "node_properties": {"content": json.dumps(node)},
            "children": [],
        }

    @classmethod
    def _error_node(cls, node: dict, error_message: str) -> dict:
        """
        Create an error node when processing fails.

        Args:
            node (dict): The node that caused the error.
            error_message (str): A message describing the error.

        Returns:
            dict: An error node.
        """
        return {
            "node_type": "unknown",
            "uuid": str(uuid4()),
            "node_properties": {"content": json.dumps(node), "error": error_message},
            "children": [],
        }

    def link_image_to_tree_node(self, page_node: dict, nearby_info_dict: dict) -> dict:
        """
        Link the image to the tree node

        - Loop the children of the page node
        - If the text block is highly similar to the content, add the uuid to the nearby_info_dict

        Match method:
            − exact match
            - fuzzy match

        Args:
            page_node (dict): The page node
            nearby_info_dict (dict): The nearby info dict

        Returns:
            nearby_info_dict (dict): The updated nearby info dict
        """

        if "children" not in page_node:
            return nearby_info_dict
        for child in page_node["children"]:
            # get the text
            content = child["node_properties"].get("content", "")
            nearby_info_dict = self.link_image_to_tree_node(child, nearby_info_dict)
            if content.strip() == "":
                continue
            for key, value in nearby_info_dict.items():
                if content.strip() == value["content"].strip():
                    value["uuids"].append(child["uuid"])
                elif self.text_bert_match(content, value["content"]):
                    value["uuids"].append(child["uuid"])

        return nearby_info_dict

    def text_bert_match(
        self, text1: str, text2: str, threshold_value: float = 0.8
    ) -> bool:
        """
        Fuzzy match the text

        Args:
            text1 (str): The first text
            text2 (str): The second text
            threshold_value (float): The threshold value

        Returns:
            bool: Whether the text is similar
        """
        embedding1 = self.sentence_transformer.encode([text1])
        embedding2 = self.sentence_transformer.encode([text2])
        similarity = self.sentence_transformer.similarity(embedding1, embedding2)

        # get the first value from the similarity matrix, and to float
        similarity = similarity[0].item()
        matched = similarity > threshold_value

        if matched:
            logger.debug(f"Matched: {text1} | {text2}")
            logger.debug(f"Similarity: {similarity}")
        return matched
