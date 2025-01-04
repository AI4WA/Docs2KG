from pathlib import Path
from typing import Any, Dict, Union

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import ImageRefMode
from loguru import logger

from Docs2KG.digitization.base import DigitizationBase
from Docs2KG.utils.config import PROJECT_CONFIG

IMAGE_RESOLUTION_SCALE = 2.0


class PDFDocling(DigitizationBase):
    """
    Enhanced PDFDocling class with separate exports for markdown, images, and tables.
    """

    def __init__(self, file_path: Path):
        super().__init__(file_path=file_path, supported_formats=[InputFormat.PDF])
        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
        pipeline_options.generate_page_images = True
        pipeline_options.generate_picture_images = True

        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

    @staticmethod
    def validate_input(input_data: Union[str, Path]) -> bool:
        try:
            if isinstance(input_data, str) and input_data.startswith(
                ("http://", "https://")
            ):
                return input_data.lower().endswith(".pdf")
            path = Path(input_data)
            return path.exists() and path.suffix.lower() == ".pdf"
        except Exception as e:
            logger.exception(f"Error validating input: {str(e)}")
            return False

    def export_markdown(self, document) -> Path:
        """Export document content to markdown file."""
        markdown_path = self.output_dir / f"{self.filename}.md"
        document.save_as_markdown(
            markdown_path,
            image_mode=ImageRefMode.REFERENCED,
            artifacts_dir=self.output_dir / "images",
        )
        return markdown_path

    def process(self) -> Dict[str, Any]:
        """
        Process PDF document and generate all outputs.
        """
        if not self.validate_input(self.file_path):
            raise ValueError(
                f"Invalid input: {self.file_path}. Expected valid PDF file path or URL"
            )

        try:
            # Convert the document
            result = self.converter.convert(str(self.file_path))

            # Generate all outputs
            markdown_path = self.export_markdown(result.document)
            return markdown_path

        except FileNotFoundError:
            raise FileNotFoundError(f"PDF source not found: {self.file_path}")
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")

    def __repr__(self) -> str:
        return f"PDFDocling(file_path='{self.file_path}')"


if __name__ == "__main__":
    # Example usage
    # pdf_path = PROJECT_CONFIG.data.input_dir / "2405.14831v1.pdf"
    pdf_path = PROJECT_CONFIG.data.input_dir / "gsdRec_2024_08.pdf"
    processor = PDFDocling(file_path=pdf_path)
    processor.process()
