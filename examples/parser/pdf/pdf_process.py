from Docs2KG.parser.pdf.pdf2images import PDF2Images
from Docs2KG.parser.pdf.pdf2tables import PDF2Tables
from Docs2KG.parser.pdf.pdf2text import PDF2Text
from Docs2KG.parser.pdf.pdf_type import PDF_TYPE_SCANNED, get_pdf_type
from Docs2KG.utils.constants import DATA_INPUT_DIR
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    pdf_file = DATA_INPUT_DIR / "4.pdf"
    pdf_type = get_pdf_type(pdf_file)
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
