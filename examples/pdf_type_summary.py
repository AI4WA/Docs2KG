from Docs2KG.parser.pdf.pdf2text import PDF2Text
from Docs2KG.parser.pdf.pdf2images import PDF2Images
from Docs2KG.parser.pdf.pdf2tables import PDF2Tables
from Docs2KG.parser.pdf.pdf_type import check_pdf_type, PDF_TYPE_SCANNED
from Docs2KG.utils.constants import DATA_INPUT_DIR
from pathlib import Path
from Docs2KG.utils.get_logger import get_logger
import argparse

logger = get_logger(__name__)

if __name__ == "__main__":
    """
    Loop a folder of pdf files and process them
    """

    args = argparse.ArgumentParser()
    args.add_argument(
        "--input_dir",
        type=str,
        help="Input directory of pdf files",
        default=DATA_INPUT_DIR,
    )
    args = args.parse_args()
    data_input_dir = Path(args.input_dir)
    total_counter = 0
    scanned_counter = 0
    for pdf_file in data_input_dir.rglob("*.pdf"):
        total_counter += 1
        pdf_type = check_pdf_type(pdf_file)
        if pdf_type == PDF_TYPE_SCANNED:
            logger.info(f"{pdf_file} is a scanned pdf, can not process it now")
            scanned_counter += 1
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
    logger.info(f"Total pdf files: {total_counter}")
    logger.info(f"Scanned pdf files: {scanned_counter}")
