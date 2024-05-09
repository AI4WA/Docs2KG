import fitz
from BlackSwan.utils.get_logger import get_logger

logger = get_logger(__name__)

PDF_TYPE_SCANNED = "scanned"
PDF_TYPE_EXPORTED = "exported"


def check_pdf_type(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    metadata = doc.metadata
    if "scan" in str(metadata).lower():
        return PDF_TYPE_SCANNED
    return PDF_TYPE_EXPORTED
