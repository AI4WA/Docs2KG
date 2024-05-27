import fitz
import pandas as pd
import pymupdf4llm

from Docs2KG.parser.pdf.base import PDFParserBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class PDF2Text(PDFParserBase):
    def __init__(self, *args, **kwargs):
        """
        Initialize the PDF2Text class

        """
        super().__init__(*args, **kwargs)

        self.text_output_dir = self.output_dir / "texts"
        self.text_output_dir.mkdir(parents=True, exist_ok=True)

    def extract2text(self, output_csv: bool = False) -> dict:
        """
        Extract text from the pdf file

        Args
        output_csv (bool, optional): Whether to output the extracted data to a csv file. Defaults to False.

        Returns:
            text (str): The extracted text
            output_file (Path): The path to the output file
            df (pd.Dataframe): The dataframe containing the text information
        """
        doc = fitz.open(self.pdf_file)
        text = ""
        texts = []
        for page in doc:
            text += page.get_text()
            texts.append({"page_number": page.number, "text": page.get_text()})

        df = pd.DataFrame(texts)
        if output_csv:
            df.to_csv(self.text_output_dir / "text.csv", index=False)
            return {
                "text": text,
                "output_file": self.text_output_dir / "text.csv",
                "df": df,
            }
        return {"text": text, "output_file": None, "df": df}

    def extract2markdown(self, output_csv: bool = False) -> dict:
        """
        Convert the extracted text to markdown

        Args:
            output_csv (bool, optional): Whether to output the extracted data to a csv file. Defaults to False.

        Returns:
            md (str): The Markdown text,
            output_file (Path): Where the Markdown text save to
            df (pd.Dataframe): Each page for the Markdown text
        """
        doc = fitz.open(self.pdf_file)
        md_text = pymupdf4llm.to_markdown(doc)
        logger.debug(f"Markdown text: {md_text}")

        # split the Markdown text into pages
        markdown_texts = []
        for page in doc:
            page_text = pymupdf4llm.to_markdown(doc=doc, pages=[page.number])
            logger.debug(f"Page {page.number} Markdown text: {page_text}")
            markdown_texts.append({"page_number": page.number, "text": page_text})
        df = pd.DataFrame(markdown_texts)

        if output_csv:
            df.to_csv(self.text_output_dir / "md.csv", index=False)
            return {
                "md": md_text,
                "output_file": self.text_output_dir / "md.csv",
                "df": df,
            }

        return {"md": md_text, "df": df, "output_file": None}
