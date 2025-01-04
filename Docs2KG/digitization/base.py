"""
Base class for digitization methods that handles conversion of various input formats
into standardized digital representations.
"""

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from Docs2KG.utils.config import PROJECT_CONFIG


class DigitizationBase(ABC):
    """
    Abstract base class for digitization agents that defines the common interface
    and functionality for all digitization implementations.

    Attributes:
        name (str): Unique identifier for the digitization agent
        supported_formats (List[str]): List of input formats this agent can process

    The output will be export to
    - markdown
    - json for table
    - json for images and files
    """

    def __init__(
        self,
        file_path: Path,
        supported_formats: Optional[List[str]] = None,
    ):
        self.file_path = file_path
        self.filename = file_path.stem
        self.name = self.__class__.__name__
        self.supported_formats = supported_formats or []

    @property
    def output_dir(self) -> Path:
        """
        Get the output directory for the digitization agent.

        Returns:
            str: Output directory path
        """
        output_dir_path = PROJECT_CONFIG.data.output_dir
        # based on the filename, we will create a folder
        output_dir = Path(output_dir_path) / self.filename / self.name
        output_dir.mkdir(parents=True, exist_ok=True)

        # create a sub folder for images
        images_dir = output_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    @abstractmethod
    def process(self, input_data: Any) -> Union[Dict, Any]:
        """
        Process the input data and return digitized output.

        Args:
            input_data: The data to be digitized

        Returns:
            Digitized representation of the input data

        Raises:
            NotImplementedError: If the child class doesn't implement this method
            ValueError: If input format is not supported
        """
        raise NotImplementedError("Each digitization agent must implement process()")

    def export_content_to_markdown_file(self, text: str) -> Path:
        with open(self.output_dir / f"{self.filename}.md", "w") as f:
            f.write(text)

        return self.output_dir / f"{self.filename}.md"

    def export_table_to_json_file(self, data: Dict) -> Path:
        with open(self.output_dir / f"{self.filename}_table.json", "w") as f:
            f.write(json.dumps(data, indent=4))

        return self.output_dir / f"{self.filename}_table.json"

    def export_images_to_json_file(self, data: Dict) -> Path:
        with open(self.output_dir / f"{self.filename}_images.json", "w") as f:
            f.write(json.dumps(data, indent=4))

        return self.output_dir / f"{self.filename}_images.json"

    def validate_input(self, input_data: Any) -> bool:
        """
        Validate if the input data format is supported by this agent.

        Args:
            input_data: The data to validate

        Returns:
            bool: True if input format is supported, False otherwise
        """
        return True  # Base implementation accepts all formats

    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get information about the digitization agent.

        Returns:
            Dict containing agent metadata and configuration
        """
        return {
            "name": self.__class__.__name__,
            "supported_formats": self.supported_formats,
        }

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(" f"supported_formats={self.supported_formats})"
        )

    def __str__(self) -> str:
        return f"{self.name} Digitization Agent"
