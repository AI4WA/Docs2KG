import fitz
import pandas as pd

from Docs2KG.parser.pdf.base import PDFParserBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class PDF2Tables(PDFParserBase):
    def __init__(self, *args, **kwargs):
        """
        Initialize the class with the pdf file
        """
        super().__init__(*args, **kwargs)
        self.table_output_dir = self.output_dir / "tables"
        self.table_output_dir.mkdir(parents=True, exist_ok=True)

    def extract2tables(self, output_csv: bool = False) -> pd.DataFrame:
        """
        Extract Tables from the pdf file

        Args:
            output_csv (bool, optional): Whether to output the extracted data to a csv file. Defaults to False.

        Returns:
            pd.DataFrame: The dataframe containing the table information
        """
        doc = fitz.open(self.pdf_file)  # open a document
        tables_list = []

        for page_index in range(len(doc)):  # iterate over pdf pages
            page = doc[page_index]  # get the page
            tabs = page.find_tables()
            if tabs.tables:
                logger.debug(f"Found {len(tabs.tables)} tables on page {page_index}")
                for table_index, tab in enumerate(tabs.tables, start=1):
                    # save to csv

                    filename = "page_%s-table_%s.csv" % (page_index, table_index)
                    # save it to bounding box cropped image
                    df = tab.to_pandas()
                    df.to_csv(self.table_output_dir / filename)
                    logger.debug(tab.bbox)
                    tables_list.append(
                        {
                            "page_index": page_index,
                            "table_index": table_index,
                            "bbox": tab.bbox,
                            "filename": filename,
                            "file_path": self.table_output_dir / filename,
                        }
                    )
        df = pd.DataFrame(tables_list)
        if output_csv:
            df.to_csv(self.table_output_dir / "tables.csv", index=False)
        return df
