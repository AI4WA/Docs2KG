import json
from pathlib import Path
from typing import Optional
from uuid import uuid4

import pandas as pd

from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)

HTML_TAGS = [
    "html",
    "head",
    "title",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "p",
    "a",
    "img",
    "div",
    "span",
    "table",
    "tr",
]


class LayoutKG:
    """
    Layout Knowledge Graph
    This is for one pdf file
    """

    def __init__(
        self,
        folder_path: Path,
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
        self.kg_df = pd.DataFrame(
            columns=[
                "source_node_type",
                "source_node_uuid",
                "source_node_properties",
                "edge_type",
                "edge_uuid",
                "edge_properties",
                "destination_node_type",
                "destination_node_uuid",
                "destination_node_properties",
            ]
        )
        self.metadata = json.load((self.folder_path / "metadata.json").open())

    def create_kg(self):
        """
        Create the layout knowledge graph
        """
        self.document_kg()
        self.link_image_to_page()
        self.link_table_to_page()
        self.link_image_to_context()
        self.link_table_to_context()

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
        logger.info(f"Columns: {columns}")
        # we will focus on the layout json

        for index, row in texts_json_df.iterrows():
            logger.info(f"Processing row {index}")
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

                logger.exception(e)
                break
        self.kg_json["children"] = pages_json
        self.export_kg()

    def link_image_to_page(self):
        """
        Loop the image, assign it under the proper page
        If the page not exist, then add a page node
        """
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
                },
                "children": [],
            }

            page_node["children"].append(image_node)

        self.export_kg()

    def link_table_to_page(self):
        """
        Construct the table knowledge graph
        """
        pass

    def link_image_to_context(self):
        """
        Construct the image knowledge graph
        """
        pass

    def link_table_to_context(self):
        """
        Construct the table knowledge graph
        """
        pass

    def export_kg(self) -> None:
        """
        Export the knowledge graph to json file
        """
        with open(self.kg_folder / "document_kg.json", "w") as f:
            json.dump(self.kg_json, f, indent=2)

    def load_kg(self):
        """
        Load the knowledge graph from JSON
        """
        with open(self.kg_folder / "document_kg.json", "r") as f:
            self.kg_json = json.load(f)

    @classmethod
    def recursive_layout_json(cls, layout_json: dict) -> dict:
        """
        Recursively decompose the layout json and add to proper level children

        Args:
            layout_json (dict): The layout json

        Returns:
            tree_json (dict): The tree json
        """

        try:
            tag = layout_json.get("tag", None)
            if tag == "table":
                return {
                    "node_type": layout_json["tag"],
                    "uuid": str(uuid4()),
                    "node_properties": {
                        "records": layout_json["children"],
                    },
                    "children": [],
                }
            if tag is None:
                for key in layout_json.keys():
                    if key in HTML_TAGS:
                        tag = key
                        return {
                            "node_type": tag,
                            "uuid": str(uuid4()),
                            "node_properties": {
                                "content": layout_json[tag],
                                "text": json.dumps(layout_json),
                            },
                            "children": [],
                        }

            tree_json = {
                "node_type": layout_json["tag"],
                "uuid": str(uuid4()),
                "node_properties": {
                    "content": layout_json["content"],
                },
                "children": [
                    cls.recursive_layout_json(child)
                    for child in layout_json.get("children", [])
                ],
            }
            return tree_json
        except Exception as e:
            logger.exception(e)
        return {
            "node_type": "error",
            "uuid": str(uuid4()),
            "node_properties": {
                "content": str(layout_json),
            },
            "children": [],
        }

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
        logger.info(f"Page {page_number} not found")
        return None
