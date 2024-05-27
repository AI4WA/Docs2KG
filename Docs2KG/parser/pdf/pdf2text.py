import fitz
import pandas as pd
import pymupdf4llm
from typing import Dict
from Docs2KG.parser.pdf.base import PDFParserBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class PDF2Text(PDFParserBase):

    def extract2text(self,
                     output_csv: bool = False) -> dict:
        """
        Extract text from the pdf file

        Args
        output_csv (bool, optional): Whether to output the extracted data to a csv file. Defaults to False.

        Returns:
            dict: The dictionary containing the extracted text, output file and dataframe
            | Key           | Value                           |
            |---------------|---------------------------------|
            | text          | Full text of document           |
            | output_file   | Where the full text save to     |
            | df            | [pd.Dataframe] Each page txt    |


        """
        doc = fitz.open(self.pdf_file)
        text = ""
        texts = []
        for page in doc:
            text += page.get_text()
            texts.append({
                "page_number": page.number,
                "text": page.get_text()
            })
        # output to the output directory
        output_file = self.output_dir / f"{self.pdf_file.stem}.txt"
        with open(output_file, "w") as f:
            f.write(text)
        df = pd.DataFrame(texts)
        if output_csv:
            df.to_csv(self.output_dir / f"{self.pdf_file.stem}.csv", index=False)
        return {
            "text": text,
            "output_file": output_file,
            "df": df
        }

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
