import json
from pathlib import Path
from typing import Any, Union

import numpy as np
from loguru import logger

from Docs2KG.utils.config import PROJECT_CONFIG


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle numpy types and other special objects"""

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, Path):
            return str(obj)
        if hasattr(obj, "to_json"):
            return obj.to_json()
        if hasattr(obj, "to_dict"):
            return obj.to_dict()
        return super().default(obj)


class KGConstructionBase:
    def __init__(self, project_id: str):
        self.project_id = project_id
        # create and set the project folder
        self.project_folder = PROJECT_CONFIG.data.output_dir / "projects" / project_id
        self.project_folder.mkdir(parents=True, exist_ok=True)

        # create a sub folder for layout kg
        layout_folder = self.project_folder / "layout"
        layout_folder.mkdir(parents=True, exist_ok=True)
        self.layout_folder = layout_folder
        self.entity_type_list = []

    def construct(self, docs):
        raise NotImplementedError

    def export_json(
        self, data: Any, filename: Union[str, Path], ensure_ascii: bool = False
    ) -> Path:
        """
        Export data to a JSON file with improved type handling.

        Args:
            data: The data to export
            filename: Name of the output file
            ensure_ascii: If False, allow non-ASCII characters in output

        Returns:
            Path: Path to the exported file

        Raises:
            IOError: If there's an error writing the file
            TypeError: If an object type cannot be serialized
        """
        try:
            # Ensure filename has .json extension
            if not str(filename).endswith(".json"):
                filename = str(filename) + ".json"

            # Create output directory if it doesn't exist
            self.project_folder.mkdir(parents=True, exist_ok=True)

            output_path = self.project_folder / filename

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, cls=JSONEncoder, ensure_ascii=ensure_ascii, indent=4)

            logger.info(f"Successfully exported {filename} to {self.project_folder}")
            return output_path

        except IOError as e:
            logger.error(f"Failed to write file {filename}: {str(e)}")
            raise

        except TypeError as e:
            logger.error(f"Serialization error for {filename}: {str(e)}")
            raise
