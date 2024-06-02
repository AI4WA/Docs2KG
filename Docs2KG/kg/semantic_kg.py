import json
import re
from pathlib import Path
from typing import List, Optional, Tuple

from tqdm import tqdm

from Docs2KG.modules.llm.openai_call import openai_call
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


CAPTION_KEYWORDS = [
    "fig",
    "table",
    "figure",
    "tab",
    "plate",
    "chart",
    "graph",
    "plate",
    "photo",
    "image",
    "diagram",
    "illustration",
]


class SemanticKG:
    """
    The plan is

    - We keep the layout_kg.json, and use this as the base
    - Then we start to extract the linkage
    - And then we have a semantic_kg.json

    Within this one we will have

    - source_uuid
    - source_semantic
    - predicate
    - target_uuid
    - target_semantic
    - extraction_method

    What we want to link:

    - Table to Content
        - Where this table is mentioned, which is actually finding the reference point
    - Image to Content
        - Same as table

    Discussion

    - Within Page
        - Text2KG with Named Entity Recognition
    - Across Pages
        - Summary Linkage?

    Alerts: Some of the functions will require the help of LLM
    """

    def __init__(
        self,
        folder_path: Path,
        llm_enabled: bool = False,
        input_format: str = "pdf_exported",
    ):
        """
        Initialize the SemanticKG class
        Args:
            folder_path (Path): The path to the pdf file
            llm_enabled (bool, optional): Whether to use LLM. Defaults to False.

        """
        self.folder_path = folder_path
        self.llm_enabled = llm_enabled
        self.cost = 0
        logger.info("LLM is enabled" if self.llm_enabled else "LLM is disabled")
        self.kg_folder = self.folder_path / "kg"
        if not self.kg_folder.exists():
            self.kg_folder.mkdir(parents=True, exist_ok=True)

        self.layout_kg_file = self.kg_folder / "layout_kg.json"
        # if layout_kg does not exist, then raise an error
        if not self.layout_kg_file.exists():
            raise FileNotFoundError(f"{self.layout_kg_file} does not exist")
        # load layout_kg
        self.layout_kg = self.load_kg(self.layout_kg_file)
        self.input_format = input_format

    def add_semantic_kg(self):
        """
        As discussed in the plan, we will add the semantic knowledge graph based on the layout knowledge graph

        Returns:

        """
        # we will start with the image to content
        if self.input_format == "pdf_exported":
            self.semantic_link_image_to_content()
            self.semantic_link_table_to_content()
        if self.input_format != "excel":
            self.semantic_page_summary()
        self.semantic_text2kg()

    def semantic_link_image_to_content(self):
        """
        Link the image to the content

        1. We will need to extract the image's caption and reference point
        2. Use this caption or 1.1 to search the context, link the image to where the image is mentioned

        Returns:

        """

        # first locate the image caption
        for page in self.layout_kg["children"]:
            # within the page node, then it should have the children start with the image node
            for child in page["children"]:
                if child["node_type"] == "image":
                    # child now is the image node
                    # if this child do not have children, then we will skip
                    if "children" not in child or len(child["children"]) == 0:
                        continue
                    # logger.info(child)
                    for item in child["children"]:
                        # if this is the caption, then we will extract the text
                        text = item["node_properties"]["content"]
                        if self.util_caption_detection(text):
                            logger.info(f"Figure/Caption detected: {text}")
                            # we will use this
                            child["node_properties"]["caption"] = text
                            """
                            Link the caption to where it is mentioned

                            For example, if the caption is "Figure 1.1: The distribution of the population",
                            then we will search the context
                            And found out a place indicate that: as shown in Figure 1.1,
                            the distribution of the population is ...

                            We need to find a way to match it back to the content

                            Current plan of attack, we use rule based way.

                            If there is a Figure XX, then we will search the context for Figure XX,
                            and link it back to the content
                            Because the content have not been
                            """

                            uuids, caption = self.util_caption_mentions_detect(
                                caption=text
                            )
                            logger.info(f"UUIDs: {uuids}")
                            child["node_properties"]["mentioned_in"] = uuids
                            if caption:
                                child["node_properties"]["unique_description"] = caption
                            continue

        self.export_kg()

    def semantic_link_table_to_content(self):
        """
        Link the table to the content

        So we will do the same thing first for the table

        Returns:

        """
        for page in self.layout_kg["children"]:
            # within the page node, then it should have the children start with the image node
            for child in page["children"]:
                if child["node_type"] == "table_csv":
                    # child now is the image node
                    # if this child do not have children, then we will skip
                    if "children" not in child or len(child["children"]) == 0:
                        continue
                    # logger.info(child)
                    for item in child["children"]:
                        # if this is the caption, then we will extract the text
                        text = item["node_properties"]["content"]
                        if self.util_caption_detection(text):
                            logger.info(f"Table/Caption detected: {text}")
                            # we will use this
                            child["node_properties"]["caption"] = text
                            uuids, caption = self.util_caption_mentions_detect(
                                caption=text
                            )
                            logger.info(f"UUIDs: {uuids}")
                            child["node_properties"]["mentioned_in"] = uuids
                            if caption:
                                child["node_properties"]["unique_description"] = caption
                            continue
        self.export_kg()

    def semantic_text2kg(self):
        """
        ## General Goal of this:

        - A list of triplet: (subject, predicate, object)
        - Triplets will be associated to the tree
        - Frequent subject will be merged, and linked

        Plan of attack:

        1. We need to do the Named Entity Recognition for each sentence
        2. Do NER coexist relationship
        3. Last step will be extracting the semantic NER vs NER relationship

        How to construction the relation?

        - We will grab the entities mapping to text uuid
        {
           "ner_type": {
            "entities": [uuid1, uuid2]
           }
        }

        """
        if self.llm_enabled:
            current_cost = self.cost
            # do the triple extraction
            # self.semantic_triplet_extraction(self.layout_kg)
            logger.info("Start the semantic text2kg extraction")
            nodes = self.semantic_triplet_extraction(self.layout_kg, [])
            # use tqdm to show the progress
            for node in tqdm(nodes, desc="Extracting triplets"):
                # extract the triplets from the text
                text = node["node_properties"]["content"]
                logger.debug(text)
                if text == "":
                    continue
                triplets = self.llm_extract_triplet(text)
                node["node_properties"]["text2kg"] = triplets
            self.export_kg()
            logger.info(f"LLM cost: {self.cost - current_cost}")
        else:
            # Hard to do this without LLM
            logger.info("LLM is not enabled, skip the semantic text2kg extraction")

    def semantic_triplet_extraction(self, node: dict, nodes: List[dict]):
        """
        Extract tripplets from the text

        It will update the node with the Text2KG field, add a list of triplets
        Args:
            node (dict): The node in the layout knowledge graph
            nodes (List[dict]): The list of nodes

        Returns:

        """
        for child in node["children"]:
            if "children" in child:
                nodes = self.semantic_triplet_extraction(child, nodes)
            content = child["node_properties"].get("content", "")
            if not content:
                continue
            nodes.append(child)
        return nodes

    def semantic_page_summary(self):
        """
        Summary of the page, which will have better understanding of the page.

        Not sure whether this will enhance the RAG or not.

        But will be easier for human to understand the page.

        When doing summary, also need to give up page and later page information

        Returns:

        """
        for page_index, page in enumerate(self.layout_kg["children"]):
            if page["node_type"] == "page":
                page_content = page["node_properties"]["page_text"]
                logger.debug(page_content)
                summary = self.llm_page_summary(page_content)
                page["node_properties"]["summary"] = summary

        self.export_kg()

    @staticmethod
    def load_kg(file_path: Path) -> dict:
        """
        Load the knowledge graph from JSON

        Args:
            file_path (Path): The path to the JSON file

        Returns:
            dict: The knowledge graph
        """
        with open(file_path, "r") as f:
            kg = json.load(f)
        return kg

    def export_kg(self):
        """
        Export the semantic knowledge graph to a JSON file
        """

        with open(self.layout_kg_file, "w") as f:
            json.dump(self.layout_kg, f, indent=4)

    def util_caption_detection(self, text: str) -> bool:  # noqa
        """
        Give a text, detect if this is a caption for image or table

        If it is LLM enabled, then we will use LLM to detect the caption
        If it is not LLM enabled, we use keyword match
            - Currently LLM performance not well

        Returns:

        """
        for keyword in CAPTION_KEYWORDS:
            if keyword in text.lower():
                return True
        # if self.llm_enabled:
        #     return self.llm_detect_caption(text)
        return False

    def util_caption_mentions_detect(self, caption: str) -> Tuple[List[str], str]:
        """

        First we need to find the unique description for the caption.

        For example: Plate 1.1: The distribution of the population

        Plate 1.1 is the unique description

        We will need to search the whole document to find the reference point

        Args:
            caption (str): The caption text


        Returns:
            uuids (List[str]): The list of uuids where the caption is mentioned

        """
        # first extract the unique description
        # Extract the unique description from the caption
        keyword_patten = "|".join(CAPTION_KEYWORDS)
        match = re.search(rf"(\b({keyword_patten}) \d+(\.\d+)*\b)", caption.lower())
        unique_description = None
        if match:
            unique_description = match.group(1)
        else:
            if self.llm_enabled:
                """
                Try to use LLM to do this work
                """
                unique_description = self.llm_detect_caption_mentions(caption)
                logger.info(f"Unique description: {unique_description}")

        if not unique_description:
            return []
        logger.info(f"Unique description: {unique_description}")
        mentioned_uuids = []
        # search the context
        mentioned_uuids = self.util_mentioned_uuids(
            self.layout_kg, unique_description, mentioned_uuids
        )
        return mentioned_uuids, unique_description

    def util_mentioned_uuids(
        self, node: dict, unique_description: str, uuids: List[str]
    ) -> List[str]:
        """
        Search the context for the unique description

        Args:
            node (dict): The node in the layout knowledge graph
            unique_description (str): The unique description extracted from the caption
            uuids (List[str]): The list of uuids where the unique description is mentioned

        Returns:
            uuids (List[str]): The list of uuids where the unique description is mentioned
        """
        for child in node["children"]:
            if "node_properties" in child:
                if "content" in child["node_properties"]:
                    if (
                        unique_description
                        in child["node_properties"]["content"].lower()
                    ):
                        uuids.append(child["uuid"])
            if "children" in child:
                uuids = self.util_mentioned_uuids(child, unique_description, uuids)
        return uuids

    def llm_detect_caption(self, text: str) -> bool:
        """
        Use LLM to detect whether the given text is a caption for an image or table.

        Args:
            text (str): The text to be evaluated.

        Returns:
            bool: True if the text is identified as a caption, False otherwise.
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a system that help to detect if the text is a caption for an image or table.
                                """,
                },
                {
                    "role": "user",
                    "content": f"""
                        Is the following text a caption for image or table?
                        You need to detect if the text is a caption for an image or table.

                        Please return the result in JSON format as follows:
                            - {'is_caption': 1} if it is a caption,
                            - or {'is_caption': 0} if it is not a caption.

                        Some examples are captions for images or tables:
                        - "Figure 1.1: The distribution of the population"
                        - "Table 2.1: The distribution of the population"
                        - "Plate 1.1: The distribution of the population"
                        - "Graph 1.1: The distribution of the population"

                        "{text}"
                    """,
                },
            ]
            response, cost = openai_call(messages)
            self.cost += cost
            logger.debug(f"LLM cost: {cost}, response: {response}, text: {text}")
            response_dict = json.loads(response)
            return response_dict.get("is_caption", 0) == 1
        except Exception as e:
            logger.error(f"Error in LLM caption detection: {e}")
        return False

    def llm_detect_caption_mentions(self, caption: str) -> Optional[str]:
        """
        Use LLM to detect the mentions of the given caption in the document.

        Args:
            caption (str): The caption text.

        Returns:
            List[str]: The list of uuids where the caption is mentioned.
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are an assistant that can detect the unique description
                                  of a caption in a document.
                                """,
                },
                {
                    "role": "user",
                    "content": f"""
                        Please find the unique description of the caption in the document.

                        For example, if the caption is "Plate 1.1: The distribution of the population",
                        the unique description is "Plate 1.1".

                        Given caption:

                        "{caption}"

                        Return the str within the json with the key "uid".
                    """,
                },
            ]
            response, cost = openai_call(messages)
            self.cost += cost
            logger.debug(f"LLM cost: {cost}, response: {response}, caption: {caption}")
            response_dict = json.loads(response)
            return response_dict.get("uid", "")
        except Exception as e:
            logger.error(f"Error in LLM caption mentions detection: {e}")
            logger.exception(e)
        return None

    def llm_extract_triplet(self, text) -> List[dict]:
        """
        Extract the triplet from the text
        Args:
            text (str): The text to extract the triplets from


        Returns:
            triplets (List[dict]): The list of triplets extracted from the text
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are an assistant that can extract the triplets from a given text.
                                """,
                },
                {
                    "role": "user",
                    "content": f"""
                        Please extract the triplets from the following text:

                        "{text}"

                        Return the triplets within the json with the key "triplets".
                        And the triplets should be in the format of a list of dictionaries,
                        each dictionary should have the following keys:
                        - subject
                        - subject_ner_type
                        - predicate
                        - object
                        - object_ner_type

                    """,
                },
            ]
            response, cost = openai_call(messages)
            self.cost += cost
            logger.debug(f"LLM cost: {cost}, response: {response}, text: {text}")
            response_dict = json.loads(response)
            return response_dict.get("triplets", [])
        except Exception as e:
            logger.error(f"Error in LLM triplet extraction: {e}")
        return []

    def llm_page_summary(self, page_content: str) -> str:
        """

        Args:
            page_content (str): The content of the page

        Returns:
            summary (str): The summary of the page

        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are an assistant that can summarize the content of a page.
                                """,
                },
                {
                    "role": "user",
                    "content": f"""
                        Please summarize the content of the page.

                        "{page_content}"

                        Return the summary within the json with the key "summary".
                    """,
                },
            ]
            response, cost = openai_call(messages)
            self.cost += cost
            logger.debug(
                f"LLM cost: {cost}, response: {response}, page_content: {page_content}"
            )
            response_dict = json.loads(response)
            return response_dict.get("summary", "")
        except Exception as e:
            logger.error(f"Error in LLM page summary: {e}")
        return ""
