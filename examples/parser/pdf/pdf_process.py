from Docs2KG.parser.pdf.pdf2images import PDF2Images
from Docs2KG.parser.pdf.pdf2tables import PDF2Tables
from Docs2KG.parser.pdf.pdf2text import PDF2Text
from Docs2KG.parser.pdf.pdf2metadata import PDF_TYPE_SCANNED, get_scanned_or_exported
from Docs2KG.utils.constants import DATA_INPUT_DIR
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    pdf_file = DATA_INPUT_DIR / "4.pdf"
    scanned_or_exported = get_scanned_or_exported(pdf_file)
    if scanned_or_exported == PDF_TYPE_SCANNED:
        logger.info("This is a scanned pdf, can not process it now")
    else:
        # process text
        pdf2text = PDF2Text(pdf_file)
        text = pdf2text.extract2text()
        md_text = pdf2text.extract2markdown()
        # process images
        pdf2images = PDF2Images(pdf_file)
        pdf2images.extract2images()
        # process tables
        pdf2tables = PDF2Tables(pdf_file)
        pdf2tables.extract2tables()
