import json
from pathlib import Path
from uuid import uuid4

import pandas as pd

from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


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
            logger.info(row["layout_json"])
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

        self.kg_json["children"] = pages_json
        with open(self.kg_folder / "document_kg.json", "w") as f:
            json.dump(self.kg_json, f, indent=2)

    @classmethod
    def recursive_layout_json(cls, layout_json: dict) -> dict:
        """
        Recursively decompose the layout json and add to proper level children

        Args:
            layout_json (dict): The layout json

        Returns:
            tree_json (dict): The tree json
        """
        tree_json = {
            "node_type": layout_json["tag"],
            "uuid": str(uuid4()),
            "node_properties": {
                "content": layout_json["content"],
            },
            "children": [
                cls.recursive_layout_json(child) for child in layout_json["children"]
            ],
        }

        return tree_json

    def link_image_to_page(self):
        """
        Construct the image knowledge graph
        """
        pass

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

    def export_kg(self) -> dict:
        """
        Export the knowledge graph to JSON
        """
        pass
