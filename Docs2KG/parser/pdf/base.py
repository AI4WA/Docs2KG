import shutil
from pathlib import Path

from Docs2KG.utils.constants import DATA_OUTPUT_DIR


class PDFParserBase:
    def __init__(self, pdf_file: Path, output_dir: Path = None) -> None:
        """
        Initialize the class with the pdf file

        Args:
            pdf_file (Path): The path to the pdf file
            output_dir (Path): The path to the output directory, default is None, will be default to DATA_OUTPUT_DIR

        """
        self.pdf_file = pdf_file
        self.output_dir = output_dir
        if self.output_dir is None:
            # get it to be that the input file => input folder
            pdf_file_folder = DATA_OUTPUT_DIR / pdf_file.name
            pdf_file_folder.mkdir(parents=True, exist_ok=True)
            self.output_dir = pdf_file_folder

        # copy original pdf to the output folder
        pdf_file_output = self.output_dir / pdf_file.name
        if not pdf_file_output.exists():
            shutil.copy(pdf_file, pdf_file_output)
