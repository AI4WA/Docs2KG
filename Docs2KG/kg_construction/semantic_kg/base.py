import json
from pathlib import Path
from typing import Any

from Docs2KG.kg_construction.base import KGConstructionBase
from Docs2KG.utils.config import PROJECT_CONFIG


class SemanticKGConstructionBase(KGConstructionBase):
    """
    Starting from the layout json, we will have several different ways to extract entities and relationships from the documents

    The task will typically into two parts:
    - Named Entity Recognition: extract entities from the text
        - input can be: entity list, ontology, or just description
    - Relationship Extraction: extract relationships between entities

    Input will be an array of layout json files, output will be another json with entities and relationships extracted
    """

    def __init__(self, project_id: str):
        super().__init__(project_id)

    @staticmethod
    def load_layout_kg(layout_kg_path: Path) -> dict:
        """
        Load the layout knowledge graph from a file.

        Args:
            layout_kg_path: Path to the layout knowledge graph file

        Returns:
            dict: Layout knowledge graph
        """
        if not layout_kg_path.exists():
            raise FileNotFoundError(
                f"Layout knowledge graph not found at {layout_kg_path}"
            )
        with open(layout_kg_path, "r") as file:
            layout_kg = json.load(file)
        return layout_kg

    @staticmethod
    def update_layout_kg(layout_kg_path: Path, layout_kg: dict) -> None:
        """
        Update the layout knowledge graph in a file.

        Args:
            layout_kg_path: Path to the layout knowledge graph file
            layout_kg: Layout knowledge graph to update
        """
        with open(layout_kg_path, "w") as file:
            json.dump(layout_kg, file, indent=2)

    def construct_kg(self, input_data: Any) -> None:
        """
        Construct a semantic knowledge graph from input data.

        Args:
            input_data: Input data to construct the knowledge graph
        """
        pass
