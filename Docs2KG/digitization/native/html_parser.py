import re
from pathlib import Path
from typing import Union
from urllib.parse import unquote, urlparse

import requests
from bs4 import BeautifulSoup
from loguru import logger
from markdownify import markdownify

from Docs2KG.digitization.base import DigitizationBase
from Docs2KG.utils.config import PROJECT_CONFIG


class HTMLDocling(DigitizationBase):
    """
    HTMLDocling class for processing HTML content from files or URLs to markdown.
    """

    def __init__(self, source: Union[str, Path]):
        self.is_url = isinstance(source, str) and self._is_valid_url(source)

        if self.is_url:
            # Create a filename from the URL
            url_path = urlparse(source).path
            url_filename = (
                unquote(Path(url_path).name)
                if url_path and Path(url_path).name
                else urlparse(source).netloc
            )
            self.html_filename = (
                f"{url_filename}.html"
                if not url_filename.endswith(".html")
                else url_filename
            )

            # Download and save the HTML content
            self.html_path = PROJECT_CONFIG.data.input_dir / self.html_filename
            self._download_and_save_html(source)

            # Use the saved file path as the source
            source = self.html_path

        super().__init__(
            file_path=source,
            supported_formats=["html", "htm"],
        )
        self.source = source

    def _download_and_save_html(self, url: str) -> None:
        """
        Download HTML content from URL and save to file.

        Args:
            url: URL to download from
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            # Ensure input directory exists
            PROJECT_CONFIG.data.input_dir.mkdir(parents=True, exist_ok=True)

            # Save the HTML content
            self.html_path.write_text(response.text, encoding="utf-8")
            logger.info(f"Saved HTML content to {self.html_path}")

        except Exception as e:
            raise Exception(f"Error downloading URL {url}: {str(e)}")

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception as e:  # noqa
            logger.exception(f"Error validating URL: {str(e)}")
            return False

    def validate_input(self, input_data: Union[str, Path]) -> bool:
        try:
            if isinstance(input_data, str) and self._is_valid_url(input_data):
                return True
            path = Path(input_data)
            return path.exists() and path.suffix.lower() in [".html", ".htm"]
        except Exception as e:
            logger.exception(f"Error validating input: {str(e)}")
            return False

    def clean_html(self, html_content: str) -> str:
        """
        Clean HTML content by removing styles, scripts, and unnecessary elements.
        """
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove style tags and their contents
        for style in soup.find_all("style"):
            style.decompose()

        # Remove script tags and their contents
        for script in soup.find_all("script"):
            script.decompose()

        # Remove all style attributes
        for tag in soup.find_all(True):
            if "style" in tag.attrs:
                del tag["style"]

        # Remove class and id attributes
        for tag in soup.find_all(True):
            if "class" in tag.attrs:
                del tag["class"]
            if "id" in tag.attrs:
                del tag["id"]

        # Convert back to string
        cleaned_html = str(soup)

        # Remove any remaining CSS-like content
        cleaned_html = re.sub(r"<style[^>]*>[\s\S]*?</style>", "", cleaned_html)
        cleaned_html = re.sub(r"/\*[\s\S]*?\*/", "", cleaned_html)
        cleaned_html = re.sub(r"{\s*[^}]*}", "", cleaned_html)

        return cleaned_html

    def export_markdown(self, content: str) -> Path:
        markdown_path = self.output_dir / f"{self.filename}.md"
        markdown_path.write_text(content, encoding="utf-8")
        return markdown_path

    def get_html_content(self) -> str:
        try:
            return Path(self.source).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return Path(self.source).read_text(encoding="latin-1")

    def process(self) -> Path:
        """
        Process HTML document and generate markdown output.
        """
        if not self.validate_input(self.source):
            raise ValueError(
                f"Invalid input: {self.source}. Expected valid HTML file or URL"
            )

        try:
            # Get HTML content
            html_content = self.get_html_content()

            # Clean the HTML content
            cleaned_html = self.clean_html(html_content)

            # Convert cleaned HTML to markdown
            markdown_content = markdownify(
                cleaned_html, heading_style="ATX", bullets="-", autolinks=True
            )

            # Additional cleanup of the markdown content
            # Remove empty lines between list items
            markdown_content = re.sub(r"\n\n-", "\n-", markdown_content)
            # Remove multiple consecutive empty lines
            markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)
            # Remove any remaining CSS-like content
            markdown_content = re.sub(r"(\{|\}|\[|\])[^\n]*\n", "", markdown_content)

            # Save markdown content to file
            markdown_path = self.export_markdown(markdown_content)
            return markdown_path

        except FileNotFoundError:
            raise FileNotFoundError(f"HTML file not found: {self.source}")
        except Exception as e:
            raise Exception(f"Error processing HTML: {str(e)}")

    def __repr__(self) -> str:
        source_type = "URL" if self.is_url else "file"
        return f"HTMLDocling({source_type}='{self.source}')"


if __name__ == "__main__":
    # Example usage with file
    html_path = PROJECT_CONFIG.data.input_dir / "UWA NLP-TLP Group.html"
    processor = HTMLDocling(html_path)
    processor.process()

    # Example usage with URL
    input_url = "https://nlp-tlp.org/"
    processor = HTMLDocling(input_url)
    processor.process()
