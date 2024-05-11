from pathlib import Path
from Docs2KG.utils.constants import DATA_OUTPUT_DIR


class PDFParserBase:
    def __init__(self, pdf_file: Path, output_dir: Path = None) -> None:
        """
        Initialize the class with the pdf file
        :param pdf_file: The path to the pdf file
        """
        self.pdf_file = pdf_file
        self.output_dir = output_dir
        if self.output_dir is None:
            # get it to be that the input file => input folder
            pdf_file_folder = DATA_OUTPUT_DIR / pdf_file.name
            pdf_file_folder.mkdir(parents=True, exist_ok=True)
            self.output_dir = pdf_file_folder
