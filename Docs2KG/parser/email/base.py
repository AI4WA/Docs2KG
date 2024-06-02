from pathlib import Path

from Docs2KG.utils.constants import DATA_OUTPUT_DIR
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class EmailParseBase:
    def __init__(self, email_file: Path, output_dir: Path = None):
        """
        Initialize the EmailParseBase class

        Args:
            email_file (Path): Path to the email file, end with .eml
            output_dir (Path): Path to the output directory where the converted files will be saved
        """
        self.email_file = email_file

        self.output_dir = output_dir
        if self.output_dir is None:
            email_output_folder = DATA_OUTPUT_DIR / email_file.name
            email_output_folder.mkdir(parents=True, exist_ok=True)

            self.output_dir = email_output_folder
