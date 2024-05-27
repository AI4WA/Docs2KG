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


def get_scanned_or_exported(pdf_path: Path) -> str:
    """
    Check if the PDF is scanned or exported
    If with_metadata is True, return the metadata also

    Current, we will use the keyword "scan" in the metadata to determine if the pdf is scanned or not.

    This can be extended based on the use case scenario

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


def get_metadata_for_files(
    pdf_files: list[Path], log_summary: bool = False
) -> pd.DataFrame:
    """
    Get metadata for a list of pdf files

    We will return the metadata as a DataFrame, and for further processing

    If it is set as **log_summary** -> True, we will log the summary of the metadata.

    Args:
        pdf_files (list[Path]): list of pdf files
        log_summary (bool): If True, log the summary of the metadata

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
    metadata_df["scanned_or_exported"] = metadata_df["file_path"].apply(
        get_scanned_or_exported
    )

    if log_summary:
        # log all the columns we have
        logger.info(f"All columns within Metadata:\n {metadata_df.columns.tolist()}")
        # log format column into  value|count format
        logger.info(
            f"Format Column:\n {metadata_df['format'].value_counts().to_markdown()}"
        )
        # log creator column into  value|count format
        logger.info(
            f"Creator Column:\n {metadata_df['creator'].value_counts().to_markdown()}"
        )
        # log producer column into  value|count format
        logger.info(
            f"Producer Column:\n {metadata_df['producer'].value_counts().to_markdown()}"
        )
        # log the encrypted column into  value|count format
        logger.info(
            f"Encrypted Column:\n {metadata_df['encryption'].value_counts().to_markdown()}"
        )
        # log the scanned_or_exported column into  value|count format
        logger.info(
            f"Scanned or Exported Column:\n {metadata_df['scanned_or_exported'].value_counts().to_markdown()}"
        )

    return metadata_df
