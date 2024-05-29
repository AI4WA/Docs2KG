from pathlib import Path
import json


class SemanticKG:
    def __init__(
        self,
        folder_path: Path,
    ):
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

        Args:
            folder_path (Path): The path to the pdf file

        """
        self.folder_path = folder_path
        self.kg_folder = self.folder_path / "kg"
        if not self.kg_folder.exists():
            self.kg_folder.mkdir(parents=True, exist_ok=True)

        self.semantic_kg = self.kg_folder / "semantic_kg.json"
        self.layout_kg = self.kg_folder / "layout_kg.json"
        # if layout_kg does not exist, then raise an error
        if not self.layout_kg.exists():
            raise FileNotFoundError(f"{self.layout_kg} does not exist")
        # load layout_kg
        self.layout_kg = self.load_kg(self.layout_kg)

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
