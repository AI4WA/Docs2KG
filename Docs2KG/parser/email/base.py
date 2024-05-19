from pathlib import Path

from Docs2KG.utils.constants import DATA_INPUT_DIR, DATA_OUTPUT_DIR
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class EmailParseBase:
    def __init__(
        self, email_filename: str, input_dir: Path = None, output_dir: Path = None
    ):
        """
        Initialize the EmailParseBase class
        :param email_filename: Name of the email file
        :param input_dir: Path to the input directory where the email files will be stored
        :param output_dir: Path to the output directory where the parsed email files will be saved
        """
        self.email_filename = email_filename
        self.input_dir = input_dir
        self.output_dir = output_dir
        if self.output_dir is None or self.input_dir is None:
            email_output_folder = DATA_OUTPUT_DIR / "email"
            email_input_folder = DATA_INPUT_DIR / "email"
            email_output_folder.mkdir(parents=True, exist_ok=True)
            email_input_folder.mkdir(parents=True, exist_ok=True)
            self.output_dir = email_output_folder
            self.input_dir = email_input_folder
        self.email_filepath = f"{self.input_dir}/{email_filename}"
