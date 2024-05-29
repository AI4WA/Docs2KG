from pathlib import Path

from Docs2KG.utils.constants import DATA_INPUT_DIR, DATA_OUTPUT_DIR
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class ExcelParseBase:
    def __init__(
        self, excel_filename: str, input_dir: Path = None, output_dir: Path = None
    ):
        """
        Initialize the ExcelParseBase class
        :param excel_filename: Name of the excel file
        :param input_dir: Path to the input directory where the excel files will be stored
        :param output_dir: Path to the output directory where the parsed excel files will be saved
        """
        self.excel_filename = excel_filename
        self.input_dir = input_dir
        self.output_dir = output_dir
        if self.output_dir is None or self.input_dir is None:
            excel_output_folder = DATA_OUTPUT_DIR / "excel"
            excel_input_folder = DATA_INPUT_DIR / "excel"
            excel_output_folder.mkdir(parents=True, exist_ok=True)
            excel_input_folder.mkdir(parents=True, exist_ok=True)
            self.output_dir = excel_output_folder
            self.input_dir = excel_input_folder
        self.excel_filepath = f"{self.input_dir}/{excel_filename}"
