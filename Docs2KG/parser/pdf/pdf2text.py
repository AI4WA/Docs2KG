import fitz
import pymupdf4llm

from Docs2KG.parser.pdf.base import PDFParserBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class PDF2Text(PDFParserBase):

    def extract2text_dict(self):
        """

        Returns:

        """
        doc = fitz.open(self.pdf_file)
        images = []

        for page in doc:
            text_dict = page.get_text("dict")
            """
            Example of the text_dict will be 
            
            ```json
            {
                "height": 792,
                "width": 612,
                "blocks": [ ....]
            }
            ```
            
            """
            blocks = text_dict["blocks"]
            type_0 = 0
            type_1 = 0
            type_2 = 0
            type_other = 0
            for block in blocks:
                if block["type"] == 0:

                    type_0 += 1
                elif block["type"] == 1:
                    type_1 += 1
                elif block["type"] == 2:
                    type_2 += 1
                else:
                    type_other += 1
            logger.info(f"Type 0: {type_0}, Type 1: {type_1}, Type 2: {type_2}, Type Other: {type_other}")

            # if "image" in text_dict:
            #     # save image to the output directory
            #     image = text_dict["image"]
            #     # it will be like b'\xff\xdf...'
            #     # save the bytes to the output directory
            #     image_bytes = image["image"]
            #     image_output_file = self.output_dir / f"{self.pdf_file.stem}_page_{page.number}.png"
            #     logger.info(f"Saving image to {image_output_file}")
            #     with open(image_output_file, "wb") as f:
            #         f.write(image_bytes)
            # output to json
            with open(self.output_dir / f"{self.pdf_file.stem}_page_{page.number}.json", "w") as f:
            # f.write(str(text_dict))
            # for key, value in text_dict.items():
            #     logger.info(f"key: {key}")

            break

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
            str: The markdown text
        """
        doc = fitz.open(self.pdf_file)
        md_text = pymupdf4llm.to_markdown(doc)
        logger.info(f"Markdown text: {md_text}")

        # output to the output directory
        output_file = self.output_dir / f"{self.pdf_file.stem}.md"
        with open(output_file, "w") as f:
            f.write(md_text)

        return md_text
