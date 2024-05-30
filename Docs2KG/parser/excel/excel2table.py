import pandas as pd

from Docs2KG.parser.excel.base import ExcelParseBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class Excel2Table(ExcelParseBase):
    def __init__(self, *args, **kwargs):
        """
        Initialize the Excel2Table class.
        """
        super().__init__(*args, **kwargs)
        self.table_output_dir = self.output_dir / "tables" / self.excel_filename
        self.table_output_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def find_table_start(df, min_non_nan=3):
        """
        Identify the most likely starting row of a table in a DataFrame.

        Parameters:
        df (pd.DataFrame): The DataFrame to inspect.
        min_non_nan (int): Minimum number of non-NaN values in a row to consider it as the start.

        Returns:
        int: Index of the row most likely to be the start of the table.
        """
        for i, row in df.iterrows():
            non_nan_count = row.count() - row.isna().sum()
            if non_nan_count >= min_non_nan:
                # Check if subsequent rows have similar non-NaN counts
                if df.iloc[i + 1:i + 5].apply(lambda x: x.count() - x.isna().sum(), axis=1).mean() >= min_non_nan:
                    return i
        return 0

    def extract_tables_from_excel(self):
        # A simple example to extract tables from excel
        df = pd.read_excel(self.excel_filepath, sheet_name=None)
        for sheet_name, sheet_data in df.items():
            start_row = self.find_table_start(sheet_data)
            sheet_data = sheet_data.iloc[start_row:].reset_index(drop=True)
            sheet_data.to_csv(self.table_output_dir / f"{sheet_name}.csv", index=False)
        logger.info(f"Tables extracted from {self.excel_filename}")
        return self.table_output_dir
