import pandas as pd

from Docs2KG.parser.excel.base import ExcelParseBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class Excel2Markdown(ExcelParseBase):
    def __init__(self, *args, **kwargs):
        """
        Initialize the Excel2Table class.
        """
        super().__init__(*args, **kwargs)
        self.text_output = self.output_dir / "texts"
        self.text_output.mkdir(parents=True, exist_ok=True)
        self.md_csv = self.text_output / "md.csv"

    def extract2markdown(self):
        # A simple example to extract tables from Excel
        md_csv = []
        df = pd.read_excel(self.excel_file, sheet_name=None)
        index = 0
        for sheet_name, sheet_data in df.items():
            # to markdown
            md_csv.append(
                {
                    "sheet_name": sheet_name,
                    "text": sheet_data.to_markdown(),
                    "page_number": index,
                }
            )
            index += 1
        md_df = pd.DataFrame(md_csv)
        md_df.to_csv(self.md_csv, index=False)
