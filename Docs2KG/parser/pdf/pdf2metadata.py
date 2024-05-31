from pathlib import Path

import fitz
import pandas as pd

from Docs2KG.parser.pdf.constants import (
    PDF_METADATA_SCAN_INDICATOR,
    PDF_TYPE_EXPORTED,
    PDF_TYPE_SCANNED,
)
from Docs2KG.utils.get_logger import get_logger
from Docs2KG.utils.llm.count_tokens import count_tokens
from Docs2KG.utils.llm.estimate_price import estimate_price

logger = get_logger(__name__)


def get_scanned_or_exported(pdf_path: Path) -> str:
    """
    Check if the PDF is scanned or exported
    If with_metadata is True, return the metadata also

    Current, we will use the keyword "scan" in the metadata to determine if the pdf is scanned or not.

    This can be extended based on the use case scenario

    | Key           | Value                                   |
    |---------------|-----------------------------------------|
    | producer      | producer (producing software)           |
    | format        | format: ‘PDF-1.4’, ‘EPUB’, etc.         |
    | encryption    | encryption method used if any           |
    | author        | author                                  |
    | modDate       | date of last modification               |
    | keywords      | keywords                                |
    | title         | title                                   |
    | creationDate  | date of creation                        |
    | creator       | creating application                    |
    | subject       | subject                                 |
    | text_token    | number of tokens in the text            |
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


def get_meda_for_file(pdf_file: Path) -> dict:
    """
    Get metadata for a single pdf file

    Args:
        pdf_file (Path): Path to the pdf file

    Returns:
        metadata (dict): Metadata for the pdf file
    """
    doc = fitz.open(pdf_file)
    metadata = doc.metadata
    texts = []
    for page in doc:
        texts.append(page.get_text())
    metadata["text_token"] = count_tokens(" ".join(texts))
    # estimate the price
    metadata["estimated_price_gpt35"] = estimate_price(metadata["text_token"])
    metadata["estimated_price_gpt4o"] = estimate_price(
        metadata["text_token"], model_name="gpt-4o"
    )
    metadata["estimated_price_4_turbo"] = estimate_price(
        metadata["text_token"], model_name="gpt-4-turbo"
    )
    metadata["file_path"] = pdf_file.as_posix()
    metadata["scanned_or_exported"] = get_scanned_or_exported(pdf_file)
    # to dict
    metadata = dict(metadata)
    return metadata


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
        metadata = get_meda_for_file(pdf_file)
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
        # estimate token in total
        logger.info(f"Total Token Count: {metadata_df['text_token'].sum()}")
        # estimate the price in total
        logger.info(f"Estimated Price 3.5: {metadata_df['estimated_price_3.5'].sum()}")
        logger.info(f"Estimated Price 4o: {metadata_df['estimated_price_4o'].sum()}")
        logger.info(
            f"Estimated Price 4 Turbo: {metadata_df['estimated_price_4_turbo'].sum()}"
        )

    return metadata_df
