from pathlib import Path

import fitz
import pandas as pd

from Docs2KG.parser.pdf.constants import (
    PDF_METADATA_SCAN_INDICATOR,
    PDF_TYPE_EXPORTED,
    PDF_TYPE_SCANNED,
)
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


def get_pdf_type(pdf_path: Path) -> str:
    """
    Check if the PDF is scanned or exported
    If with_metadata is True, return the metadata also

    Args:
        pdf_path (Path): Path to the pdf file

    Returns:
        str: The type of the pdf file

    """
    doc = fitz.open(pdf_path)
    metadata = doc.metadata
    logger.debug(f"Metadata: {metadata}")
    if PDF_METADATA_SCAN_INDICATOR in str(metadata).lower():
        return PDF_TYPE_SCANNED
    return PDF_TYPE_EXPORTED


def get_metadata_for_files(pdf_files: list[Path]) -> pd.DataFrame:
    """
    Get metadata for a list of pdf files
    We will return the metadata as a DataFrame, and for further processing

    Args:
        pdf_files (list[Path]): list of pdf files

    Returns:
        pd.DataFrame: DataFrame containing metadata for the pdf files
    """

    all_metadata = []
    for pdf_file in pdf_files:
        doc = fitz.open(pdf_file)
        metadata = doc.metadata
        all_metadata.append(metadata)
    metadata_df = pd.DataFrame(all_metadata)
    # add a line called "file_path" to the metadata
    metadata_df["file_path"] = pdf_files
    return metadata_df
