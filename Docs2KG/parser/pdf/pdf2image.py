import fitz
import pandas as pd

from Docs2KG.parser.pdf.base import PDFParserBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class PDF2Image(PDFParserBase):
    def __init__(self, *args, **kwargs):
        """
        Initialize the PDF2Images class

        """
        super().__init__(*args, **kwargs)
        self.images_output_dir = self.output_dir / "images"
        self.images_output_dir.mkdir(parents=True, exist_ok=True)
        self.text_output_dir = self.output_dir / "texts"
        self.text_output_dir.mkdir(parents=True, exist_ok=True)
        # clean the image folder
        for file in self.images_output_dir.glob("*"):
            # delete the file
            file.unlink()

    def extract_page_2_image_df(self):
        """
        Extract the page to image across the whole pdf, each page will be one image

        Returns:

        """
        doc = fitz.open(self.pdf_file)
        logger.info(f"Extracting data from {self.pdf_file}")
        df = pd.DataFrame()
        image_data = []

        for page in doc:
            pix = page.get_pixmap()
            image_bytes = pix.tobytes("png")
            image_path = (
                self.images_output_dir / f"page_{page.number + 1}.png"
            )  # Page numbers are 0-indexed in PyMuPDF
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            image_data.append(
                {"page_number": page.number, "image_path": str(image_path)}
            )

        df = pd.DataFrame(image_data)
        df.to_csv(self.images_output_dir / "page_images.csv", index=False)
        return df
