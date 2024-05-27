from pathlib import Path


class SemanticKG:
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
