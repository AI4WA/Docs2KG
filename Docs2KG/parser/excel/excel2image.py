import pandas as pd
from Docs2KG.parser.excel.base import ExcelParseBase
from Docs2KG.utils.get_logger import get_logger
import imgkit
import pdfkit

logger = get_logger(__name__)


class Excel2Image(ExcelParseBase):
    def __init__(self, *args, **kwargs):
        """
        Initialize the Excel2Image class.
        """
        super().__init__(*args, **kwargs)
        self.image_output_dir = self.output_dir / "images" / self.excel_filename
        self.image_output_dir.mkdir(parents=True, exist_ok=True)

    def excel2image_and_pdf(self):
        """
        Convert an Excel file to image and pdf files.
        """
        xls = pd.ExcelFile(self.excel_filepath)
        # Loop through each sheet in the Excel file
        for sheet_name in xls.sheet_names:
            # Read the sheet into a DataFrame
            df = pd.read_excel(self.excel_filepath, sheet_name=sheet_name)
            df.columns = ["" if col.startswith("Unnamed") else col for col in df.columns]
            df = df.fillna("")  # Replace NaN values with an empty string
            # Convert the DataFrame to HTML
            html = df.to_html()
            # Save the HTML to an image file
            imgkit.from_string(html, f'{self.image_output_dir}/{sheet_name}.png')
            logger.info(f"Image saved to {self.image_output_dir}/{sheet_name}.png")
            pdfkit.from_string(html, f'{self.image_output_dir}/{sheet_name}.pdf')
            logger.info(f"PDF saved to {self.image_output_dir}/{sheet_name}.pdf")
