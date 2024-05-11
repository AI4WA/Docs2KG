import fitz
from Docs2KG.utils.get_logger import get_logger
from Docs2KG.parser.pdf.constants import PDF_TYPE_SCANNED, PDF_TYPE_EXPORTED, PDF_METADATA_SCAN_INDICATOR

logger = get_logger(__name__)


def check_pdf_type(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    metadata = doc.metadata
    if PDF_METADATA_SCAN_INDICATOR in str(metadata).lower():
        return PDF_TYPE_SCANNED
    return PDF_TYPE_EXPORTED
