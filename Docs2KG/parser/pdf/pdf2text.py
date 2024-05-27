import fitz
import pymupdf4llm

from Docs2KG.parser.pdf.base import PDFParserBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class PDF2Text(PDFParserBase):

    def extract2text(self) -> str:
        """
        Extract text from the pdf file

        Returns:
            str: The extracted text

        """
        doc = fitz.open(self.pdf_file)
        text = ""
        for page in doc:
            text += page.get_text()
        # output to the output directory
        output_file = self.output_dir / f"{self.pdf_file.stem}.txt"
        with open(output_file, "w") as f:
            f.write(text)
        return text

    def extract2markdown(self) -> str:
        """
        Convert the extracted text to markdown

        Returns:
            str: The Markdown text
        """
        doc = fitz.open(self.pdf_file)
        md_text = pymupdf4llm.to_markdown(doc)
        logger.info(f"Markdown text: {md_text}")

        # output to the output directory
        output_file = self.output_dir / f"{self.pdf_file.stem}.md"
        with open(output_file, "w") as f:
            f.write(md_text)

        return md_text
