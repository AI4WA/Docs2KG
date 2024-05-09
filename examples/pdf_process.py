from BlackSwan.pdf_parser.pdf2text import PDF2Text
from BlackSwan.pdf_parser.pdf2images import PDF2Images
from BlackSwan.pdf_parser.pdf2tables import PDF2Tables
from BlackSwan.pdf_parser.pdf_type import check_pdf_type, PDF_TYPE_SCANNED
from BlackSwan.utils.constants import DATA_INPUT_DIR
from BlackSwan.utils.get_logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    pdf_file = DATA_INPUT_DIR / "4.pdf"
    pdf_type = check_pdf_type(pdf_file)
    if pdf_type == PDF_TYPE_SCANNED:
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
