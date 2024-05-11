from Docs2KG.utils.get_logger import get_logger
from Docs2KG.parser.pdf.base import PDFParserBase
import fitz

logger = get_logger(__name__)


class PDF2Images(PDFParserBase):
    def __init__(self, *args, **kwargs):
        """
        Initialize the class with the pdf file
        :param args:
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.images_output_dir = self.output_dir / "images"
        self.images_output_dir.mkdir(parents=True, exist_ok=True)

    def extract2images(self):
        """
        Extract images from the pdf file
        :return:
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
            ):  # enumerate the image list
                xref = img[0]  # get the XREF of the image
                pix = fitz.Pixmap(doc, xref)  # create a Pixmap

                if pix.n - pix.alpha > 3:  # CMYK: convert to RGB first
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                filename = "page_%s-image_%s.png" % (page_index, image_index)
                pix.save(self.images_output_dir / filename)  # save the image as png
