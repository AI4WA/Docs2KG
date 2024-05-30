from typing import Dict

import fitz
import pandas as pd

from Docs2KG.parser.pdf.base import PDFParserBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class PDF2Blocks(PDFParserBase):
    def __init__(self, *args, **kwargs):
        """
        Initialize the PDF2Images class

        """
        super().__init__(*args, **kwargs)
        self.images_output_dir = self.output_dir / "images"
        self.images_output_dir.mkdir(parents=True, exist_ok=True)
        self.text_output_dir = self.output_dir / "texts"
        self.text_output_dir.mkdir(parents=True, exist_ok=True)

    def extract_df(self, output_csv: bool = False) -> Dict[str, pd.DataFrame]:
        """
        It will extract figures and text from the pdf file and return a pandas dataframe

        Have tried to extract the page to a xhtml, however, it does not contain the hierarchy of the text information.

        Args:
            output_csv (bool, optional): Whether to output the extracted data to a csv file. Defaults to False.

        Returns:
            Dict[str, pd.DataFrame]: The dictionary containing the text and image information

        """

        doc = fitz.open(self.pdf_file)
        logger.info(f"Extracting data from {self.pdf_file}")

        images = []
        texts = []
        for page in doc:
            page_dict = page.get_text("dict")
            blocks = page_dict["blocks"]
            for block in blocks:
                if block["type"] == 0:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            span["page_number"] = page.number
                            span["block_number"] = block["number"]
                            texts.append(span)
                elif block["type"] == 1:
                    # remove "image" key from the block
                    image_bytes = block.pop("image", None)
                    block["page_number"] = page.number
                    block["block_number"] = block["number"]
                    with open(
                        self.images_output_dir
                        / f"page_{page.number}_block_{block['block_number']}.{block['ext']}",
                        "wb",
                    ) as f:
                        f.write(image_bytes)
                    block["image_path"] = (
                        self.images_output_dir
                        / f"page_{page.number}_block_{block['block_number']}.{block['ext']}"
                    )
                    images.append(block)

        texts_df = pd.DataFrame(texts)
        images_df = pd.DataFrame(images)
        if output_csv:
            texts_df.to_csv(self.text_output_dir / "blocks_texts.csv", index=False)
            images_df.to_csv(self.images_output_dir / "blocks_images.csv", index=False)
        return {
            "texts": texts_df,
            "images": images_df,
            "file_name": self.pdf_file.name,
            "file_path": self.pdf_file,
            "pages_no": len(doc),
            "file_type": "exported_pdf",
            "file_size": self.pdf_file.stat().st_size,
        }
