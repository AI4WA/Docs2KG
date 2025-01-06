from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import ebooklib
import html2text
from bs4 import BeautifulSoup
from ebooklib import epub
from loguru import logger

from Docs2KG.digitization.base import DigitizationBase
from Docs2KG.utils.config import PROJECT_CONFIG


@dataclass
class Chapter:
    """Data class for storing chapter information"""

    title: str
    content: str
    order: int
    images: List[Dict[str, str]]


class EPUBDigitization(DigitizationBase):
    """
    EPUB digitization agent that converts EPUB files to markdown, extracts images,
    and generates structured data.

    Inherits from DigitizationBase and implements EPUB-specific processing logic.
    """

    def __init__(self, file_path: Path):
        super().__init__(file_path=file_path, supported_formats=["epub"])
        self.book = None
        self.chapters: List[Chapter] = []
        self.metadata: Dict[str, Any] = {}
        self.image_counter = 0

        # Configure HTML to Text converter
        self.text_maker = html2text.HTML2Text()
        self.text_maker.ignore_links = False
        self.text_maker.ignore_images = False
        self.text_maker.body_width = 0

    def validate_input(self, input_data: Union[str, Path]) -> bool:
        """
        Validate if the input is a valid EPUB file.

        Args:
            input_data: File path to validate

        Returns:
            bool: True if input is valid EPUB, False otherwise
        """
        try:
            path = Path(input_data)
            if not path.exists():
                logger.error(f"File not found: {path}")
                return False

            if path.suffix.lower() != ".epub":
                logger.error(f"Invalid file format: {path.suffix}")
                return False

            # Try to load the EPUB file
            epub.read_epub(str(path))
            return True

        except Exception as e:
            logger.error(f"Error validating EPUB: {str(e)}")
            return False

    def extract_images_from_chapter(
        self, chapter_content: str, chapter_id: str
    ) -> List[Dict[str, str]]:
        """
        Extract and save images from chapter content.

        Args:
            chapter_content: HTML content of the chapter
            chapter_id: Identifier for the chapter

        Returns:
            List of dictionaries containing image information
        """
        images = []
        soup = BeautifulSoup(chapter_content, "html.parser")

        for img in soup.find_all("img"):
            try:
                img_src = img.get("src", "")
                if not img_src:
                    continue

                self.image_counter += 1
                img_filename = f"image_{chapter_id}_{self.image_counter}.jpg"
                img_path = self.output_dir / "images" / img_filename

                for item in self.book.get_items_of_type(ebooklib.ITEM_IMAGE):
                    if item.file_name.endswith(img_src.split("/")[-1]):
                        with open(img_path, "wb") as f:
                            f.write(item.content)

                        images.append(
                            {
                                "original_src": img_src,
                                "saved_path": str(
                                    img_path.relative_to(self.output_dir)
                                ),
                                "alt_text": img.get("alt", ""),
                                "chapter_id": chapter_id,
                            }
                        )

                        img["src"] = str(img_path.relative_to(self.output_dir))

            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")

        return images

    def process_chapter(self, chapter_item, order: int) -> Optional[Chapter]:
        """
        Process a single chapter from the EPUB.

        Args:
            chapter_item: EpubItem containing chapter content
            order: Chapter order number

        Returns:
            Chapter object or None if processing fails
        """
        try:
            content = chapter_item.get_content().decode("utf-8")
            soup = BeautifulSoup(content, "html.parser")

            title = soup.find("title")
            title = title.text if title else f"Chapter {order}"

            images = self.extract_images_from_chapter(content, f"ch{order}")
            markdown_content = self.text_maker.handle(str(soup))

            return Chapter(
                title=title, content=markdown_content, order=order, images=images
            )

        except Exception as e:
            logger.error(f"Error processing chapter: {str(e)}")
            return None

    def extract_metadata(self):
        """Extract metadata from the EPUB file."""
        try:
            self.metadata = {
                "title": self.book.get_metadata("DC", "title"),
                "creator": self.book.get_metadata("DC", "creator"),
                "language": self.book.get_metadata("DC", "language"),
                "publisher": self.book.get_metadata("DC", "publisher"),
                "identifier": self.book.get_metadata("DC", "identifier"),
                "date": self.book.get_metadata("DC", "date"),
            }

            # Clean up metadata values
            for key, value in self.metadata.items():
                if isinstance(value, list) and value:
                    self.metadata[key] = value[0][0]
                elif not value:
                    self.metadata[key] = None

        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")

    def process(self, input_data: Optional[Any] = None) -> Dict[str, Any]:
        """
        Process the EPUB file and generate all outputs.

        Args:
            input_data: Optional additional input data (not used in this implementation)

        Returns:
            Dictionary containing paths to generated outputs
        """
        if not self.validate_input(self.file_path):
            raise ValueError(f"Invalid EPUB file: {self.file_path}")

        try:
            # Read the EPUB file
            self.book = epub.read_epub(str(self.file_path))

            # Extract metadata
            self.extract_metadata()

            # Process chapters
            all_images = []
            markdown_content = []

            # Add metadata section
            markdown_content.append("---")
            for key, value in self.metadata.items():
                if value:
                    markdown_content.append(f"{key}: {value}")
            markdown_content.append("---\n")

            # Process chapters and collect content
            for idx, item in enumerate(
                self.book.get_items_of_type(ebooklib.ITEM_DOCUMENT)
            ):
                chapter = self.process_chapter(item, idx)
                if chapter:
                    self.chapters.append(chapter)
                    markdown_content.extend(
                        [f"# {chapter.title}\n", chapter.content, "---\n"]
                    )
                    all_images.extend(chapter.images)

            # Export markdown content
            markdown_path = self.export_content_to_markdown_file(
                "\n".join(markdown_content)
            )

            # Export images data
            images_data = {"total_images": len(all_images), "images": all_images}
            images_json_path = self.export_images_to_json_file(images_data)

            # Export basic structure data as table
            structure_data = {
                "metadata": self.metadata,
                "chapters": [
                    {
                        "title": ch.title,
                        "order": ch.order,
                        "image_count": len(ch.images),
                    }
                    for ch in self.chapters
                ],
            }
            table_json_path = self.export_table_to_json_file(structure_data)

            return {
                "markdown_path": markdown_path,
                "images_json_path": images_json_path,
                "table_json_path": table_json_path,
                "total_chapters": len(self.chapters),
                "total_images": len(all_images),
            }

        except Exception as e:
            logger.error(f"Error processing EPUB: {str(e)}")
            raise


if __name__ == "__main__":
    # Example usage
    epub_path = PROJECT_CONFIG.data.input_dir / "pg75033-images.epub"
    processor = EPUBDigitization(file_path=epub_path)

    try:
        result = processor.process()
        logger.info("Processing complete!")
        logger.info(f"Markdown file: {result['markdown_path']}")
        logger.info(f"Images JSON: {result['images_json_path']}")
        logger.info(f"Structure JSON: {result['table_json_path']}")
        logger.info(f"Total chapters: {result['total_chapters']}")
        logger.info(f"Total images: {result['total_images']}")
    except Exception as e:
        logger.info(f"Error processing EPUB: {e}")
