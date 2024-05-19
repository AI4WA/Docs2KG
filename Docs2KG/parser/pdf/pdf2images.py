import fitz

from Docs2KG.parser.pdf.base import PDFParserBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class PDF2Images(PDFParserBase):
    def __init__(self, *args, **kwargs):
        """
        Initialize the PDF2Images class

        """
        super().__init__(*args, **kwargs)
        self.images_output_dir = self.output_dir / "images"
        self.images_output_dir.mkdir(parents=True, exist_ok=True)

    def extract2images(self):
        """
        Extract images from the pdf file
        """
        doc = fitz.open(self.pdf_file)  # open a document

        for page_index in range(len(doc)):  # iterate over pdf pages
            page = doc[page_index]  # get the page
            image_list = page.get_images(full=True)

            # print the number of images found on the page
            if image_list:
                logger.info(f"Found {len(image_list)} images on page {page_index}")
            else:
                logger.info(f"No images found on page {page_index}")

            for image_index, img in enumerate(
                    image_list, start=1
            ):  # list the image list
                xref = img[0]  # get the XREF of the image
                pix = fitz.Pixmap(doc, xref)  # create a Pixmap

                if pix.n - pix.alpha > 3:  # CMYK: convert to RGB first
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                filename = "page_%s-image_%s.png" % (page_index, image_index)
                pix.save(self.images_output_dir / filename)  # save the image as png
