from pathlib import Path
import json
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
        self.df = pd.DataFrame(
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
        text_folder = self.folder_path / "texts"
        md_json_csv = text_folder / "md.json.csv"
        texts_json_df = pd.read_csv(md_json_csv)
        columns = texts_json_df.columns.tolist()
        logger.info(f"Columns: {columns}")
        # we will focus on the layout json

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
