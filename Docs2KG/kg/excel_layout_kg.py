import json
from pathlib import Path
from uuid import uuid4

import pandas as pd
from sentence_transformers import SentenceTransformer

from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class ExcelLayoutKG:
    """
    Layout Knowledge Graph
    For each excel, each sheet will be a node (same a page in pdf)
    Then we will have the images and tables connect to the sheet, also the
    summary and description will be added to the sheet node

    """

    def __init__(
        self,
        folder_path: Path,
        input_format: str = "pdf_exported",
    ):
        """
        Initialize the class with the pdf file
        The goal of this is to construct the layout knowledge graph

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

    def document_kg(self):
        """
        Construct the layout knowledge graph skeleton first

        We will require the md.json.csv file with the following columns:

        - layout_json
        """
        # 1. add the document node

        self.kg_json = {
            "node_type": "excel",
            "uuid": str(uuid4()),
            "node_properties": self.metadata,
            "children": [],
        }

        # 2. add page nodes
        pages_json = []
        text_folder = self.folder_path / "texts"
        md_json_csv = text_folder / "md.json.csv"
        summary_and_desc_df = pd.read_csv(md_json_csv)
        columns = summary_and_desc_df.columns.tolist()
        logger.debug(f"Columns: {columns}")
        # we will focus on the layout json
        table_df = pd.read_csv(self.folder_path / "tables" / "tables.csv")
        image_df = pd.read_csv(self.folder_path / "images" / "images.csv")

        for index, row in summary_and_desc_df.iterrows():
            logger.info(f"Processing page_index {index}")
            try:
                # get table_item
                table_item = table_df[table_df["page_index"] == index]
                image_item = image_df[image_df["page_index"] == index]
                page_json = {
                    "node_type": "page",
                    "uuid": str(uuid4()),
                    "node_properties": {
                        "page_number": row["page_number"],
                        "page_text": row["text"],
                        "sheet_name": row["sheet_name"],
                        "summary": row["summary"] if pd.notna(row["summary"]) else "",
                        "content": row["desc"] if pd.notna(row["desc"]) else "",
                    },
                    "children": [
                        # we will have image node, table node
                        {
                            "node_type": "table_csv",
                            "uuid": str(uuid4()),
                            "node_properties": {
                                "table_path": table_item["file_path"].values[0],
                                "table_index": int(table_item["table_index"].values[0]),
                            },
                            "children": [],
                        },
                        {
                            "node_type": "image",
                            "uuid": str(uuid4()),
                            "node_properties": {
                                "image_path": image_item["file_path"].values[0],
                                "filename": image_item["filename"].values[0],
                            },
                            "children": [],
                        },
                    ],
                }
                pages_json.append(page_json)
            except Exception as e:
                logger.error(f"Error in row {index}: {e}")

                logger.exception(e)
                # if this is an unhandled error
                # we should still keep all data for this page, so we will construct a page with everything we have
                page_json = {
                    "node_type": "page",
                    "uuid": str(uuid4()),
                    "node_properties": {
                        "page_number": row["page_number"],
                        "page_text": row["text"],
                        "sheet_name": row["sheet_name"],
                        "summary": row["summary"] if pd.notna(row["summary"]) else "",
                        "content": row["desc"] if pd.notna(row["desc"]) else "",
                    },
                    "children": [],
                }
                pages_json.append(page_json)

        self.kg_json["children"] = pages_json
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
