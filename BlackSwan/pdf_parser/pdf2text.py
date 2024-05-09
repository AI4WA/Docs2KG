import pymupdf4llm
import fitz
from BlackSwan.utils.get_logger import get_logger
from BlackSwan.pdf_parser.base import PDFParserBase

logger = get_logger(__name__)


class PDF2Text(PDFParserBase):
    def extract2text(self) -> str:
        """
        Extract text from the pdf file
        :return: The extracted text
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
        :return: The markdown text
        """
        doc = fitz.open(self.pdf_file)
        md_text = pymupdf4llm.to_markdown(doc)
        logger.info(f"Markdown text: {md_text}")

        # output to the output directory
        output_file = self.output_dir / f"{self.pdf_file.stem}.md"
        with open(output_file, "w") as f:
            f.write(md_text)

        return md_text
