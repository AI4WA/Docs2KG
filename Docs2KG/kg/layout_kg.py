from pathlib import Path
import pandas as pd


class LayoutKG:
    """
    Layout Knowledge Graph
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
        Construct the text knowledge graph
        """
        pass

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
