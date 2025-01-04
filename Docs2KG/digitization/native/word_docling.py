from pathlib import Path
from typing import Union

import mammoth
from loguru import logger

from Docs2KG.digitization.base import DigitizationBase
from Docs2KG.utils.config import PROJECT_CONFIG


class DOCXMammoth(DigitizationBase):
    """
    DOCXDocling class for processing Word documents using mammoth.
    """

    def __init__(self, file_path: Path):
        super().__init__(file_path=file_path, supported_formats=["docx"])

    @staticmethod
    def validate_input(input_data: Union[str, Path]) -> bool:
        """
        Validate if the input is a valid DOCX file path.

        Args:
            input_data: Path to DOCX file (string or Path object)

        Returns:
            bool: True if input is valid DOCX file, False otherwise
        """
        try:
            path = Path(input_data)
            return path.exists() and path.suffix.lower() == ".docx"
        except Exception as e:
            logger.exception(f"Error validating input: {str(e)}")
            return False

    def export_markdown(self, content: str) -> Path:
        """
        Export content to markdown file.

        Args:
            content: The markdown content to export

        Returns:
            Path: Path to the generated markdown file
        """
        markdown_path = self.output_dir / f"{self.filename}.md"
        markdown_path.write_text(content, encoding="utf-8")
        return markdown_path

    def process(self) -> Path:
        """
        Process DOCX document and generate markdown output.

        Returns:
            Path: Path to the generated markdown file

        Raises:
            ValueError: If input is not a valid DOCX file
            FileNotFoundError: If DOCX file doesn't exist
        """
        if not self.validate_input(self.file_path):
            raise ValueError(
                f"Invalid input: {self.file_path}. Expected valid DOCX file"
            )

        try:
            # Convert DOCX to markdown using mammoth
            with open(self.file_path, "rb") as docx_file:
                result = mammoth.convert_to_markdown(docx_file)
                markdown_content = result.value

                # Log any conversion messages
                if result.messages:
                    for message in result.messages:
                        logger.info(f"Conversion message: {message}")

            # Save markdown content to file
            markdown_path = self.export_markdown(markdown_content)
            return markdown_path

        except FileNotFoundError:
            raise FileNotFoundError(f"DOCX file not found: {self.file_path}")
        except Exception as e:
            raise Exception(f"Error processing DOCX: {str(e)}")

    def __repr__(self) -> str:
        return f"DOCXDocling(file_path='{self.file_path}')"


if __name__ == "__main__":
    # Example usage
    docx_path = PROJECT_CONFIG.data.input_dir / "Basic modern cover letter.docx"
    processor = DOCXMammoth(file_path=docx_path)
    processor.process()
