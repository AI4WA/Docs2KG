import argparse
from pathlib import Path

from Docs2KG.parser.pdf.pdf2metadata import get_metadata_for_files
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
    all_metadata_df = get_metadata_for_files(all_files, log_summary=True)
    # then you can save it to a file
    all_metadata_df.to_csv(DATA_OUTPUT_DIR / "metadata.csv", index=False)
    # or use can use the metadata as the orchestrator
    # so files can be directed to different processing pipelines
    # and modules based on the metadata
