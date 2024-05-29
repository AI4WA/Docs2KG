import pandas as pd
from Docs2KG.parser.excel.base import ExcelParseBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class Excel2Table(ExcelParseBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table_output_dir = self.output_dir / "tables" / self.excel_filename
        self.table_output_dir.mkdir(parents=True, exist_ok=True)

    def extract_tables_from_excel(self):
        # A simple example to extract tables from excel
        df = pd.read_excel(self.excel_filepath, sheet_name=None)
        for sheet_name, sheet_data in df.items():
            sheet_data.to_csv(self.table_output_dir / f"{sheet_name}.csv", index=False)
        logger.info(f"Tables extracted from {self.excel_filename}")
        return self.table_output_dir
