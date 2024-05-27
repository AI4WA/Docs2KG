import fitz

from Docs2KG.parser.pdf.base import PDFParserBase
from Docs2KG.utils.get_logger import get_logger
import pandas as pd

logger = get_logger(__name__)


class PDF2Images(PDFParserBase):
    """
    For the machine generated and exported pdf files, we can extract the images from the pdf files.

    This will be the module to implement it.

    It will take in an input pdf file path, and an output folder path to save the images.

    Extract functions, will do the processing

    - Export the images to the path
    - Extract the meta information about the images
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the PDF2Images class

        """
        super().__init__(*args, **kwargs)
        self.images_output_dir = self.output_dir / "images"
        self.images_output_dir.mkdir(parents=True, exist_ok=True)

    def extract2images(self) -> pd.DataFrame:
        """
        Extract images from the pdf file

        The images will be cropped and then saved to the output directory

        Aim for us is:
        - To extract the images from the pdf file
        - Get the position information of the images
        - Get the context of the image, what's the paragraph before and after it.

        Returns:
            pd.DataFrame: The dictionary containing the image information
        """

        images_metadata = []
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
                logger.info(img)

                pix = fitz.Pixmap(doc, xref)  # create a Pixmap
                logger.info(pix)

                if pix.n - pix.alpha > 3:  # CMYK: convert to RGB first
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                filename = "page_%s-image_%s.png" % (page_index, image_index)
                pix.save(self.images_output_dir / filename)  # save the image as png

                # save the metadata
                image_metadata = {
                    "page_index": page_index,
                    "image_index": image_index,
                    "filename": filename,
                    "image_width": pix.width,
                    "image_height": pix.height,
                    "image_colorspace": pix.n,
                    "image_alpha": pix.alpha,

                }

                logger.info(image_metadata)
                images_metadata.append(image_metadata)

        images_metadata_df = pd.DataFrame(images_metadata)
        return images_metadata_df
