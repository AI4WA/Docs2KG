import json
from pathlib import Path

from Docs2KG.modules.llm.openai_call import openai_call
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


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

        self.semantic_kg_file = self.kg_folder / "semantic_kg.json"
        self.layout_kg_file = self.kg_folder / "layout_kg.json"
        # if layout_kg does not exist, then raise an error
        if not self.layout_kg_file.exists():
            raise FileNotFoundError(f"{self.layout_kg_file} does not exist")
        # load layout_kg
        self.layout_kg = self.load_kg(self.layout_kg_file)
        self.semantic_kg = {}

    def add_semantic_kg(self):
        """
        As discussed in the plan, we will add the semantic knowledge graph based on the layout knowledge graph

        Returns:

        """
        # we will start with the image to content
        self.semantic_link_image_to_content()
        self.semantic_link_table_to_content()
        self.semantic_text2kg()
        self.semantic_page_summary_linkage()

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
                        if self.caption_detection(text):
                            logger.info(f"Caption detected: {text}")
                            # we will use this
                            child["node_properties"]["caption"] = text
                            continue

        self.export_kg("layout")

    def semantic_link_table_to_content(self):
        """
        Link the table to the content

        Returns:

        """
        pass

    def semantic_text2kg(self):
        """
        Link the text to the knowledge graph

        Returns:

        """
        pass

    def semantic_page_summary_linkage(self):
        """
        Link the summary across pages

        Returns:

        """
        pass

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

    def export_kg(self, kg_type: str):
        """
        Export the semantic knowledge graph to a JSON file
        """
        if kg_type == "semantic":
            with open(self.semantic_kg_file, "w") as f:
                json.dump(self.semantic_kg, f, indent=4)
        elif kg_type == "layout":
            with open(self.layout_kg_file, "w") as f:
                json.dump(self.layout_kg, f, indent=4)

    def caption_detection(self, text: str) -> bool:  # noqa
        """
        Give a text, detect if this is a caption for image or table

        If it is LLM enabled, then we will use LLM to detect the caption
        If it is not LLM enabled, we use keyword match
            - Currently LLM performance not well

        Returns:

        """
        caption_keywords = ["fig", "table", "figure", "tab", "plate", "chart", "graph"]
        for keyword in caption_keywords:
            if keyword in text.lower():
                return True
        # if self.llm_enabled:
        #     return self.llm_detect_caption(text)
        return False

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
                    "content": """You are a system that detects if a given text is a caption for an image or table.
                                  Please return the result in JSON format as follows:
                                  - {'is_caption': 1} if it is a caption, 
                                  - or {'is_caption': 0} if it is not a caption.
                                """,
                },
                {
                    "role": "user",
                    "content": f"""
                        Is the following text a caption for image or table?
    
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
