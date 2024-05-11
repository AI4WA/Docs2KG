import argparse
from pathlib import Path

import pandas as pd

from Docs2KG.parser.pdf.constants import PDF_TYPE_SCANNED
from Docs2KG.parser.pdf.pdf2images import PDF2Images
from Docs2KG.parser.pdf.pdf2tables import PDF2Tables
from Docs2KG.parser.pdf.pdf2text import PDF2Text
from Docs2KG.parser.pdf.pdf_type import get_metadata_for_files, get_pdf_type
from Docs2KG.utils.constants import DATA_INPUT_DIR, DATA_OUTPUT_DIR
from Docs2KG.utils.get_logger import get_logger

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
    all_files = list(data_input_dir.rglob("*.pdf"))
    all_metadata = get_metadata_for_files(all_files)
    all_metadata.to_csv(DATA_OUTPUT_DIR / "metadata.csv", index=False)
    # format distribution
    logger.info(all_metadata["format"].value_counts())
    logger.info(all_metadata["creator"].value_counts())

    producer_value_counts = all_metadata["producer"].value_counts().items()
    number_of_producers = 0
    for producer, count in producer_value_counts:
        logger.info(f"Producer: {producer}, count: {count}")
        number_of_producers += 1
    logger.info(f"Number of producers: {number_of_producers}")
