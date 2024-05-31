import pandas as pd
from bs4 import BeautifulSoup

from Docs2KG.parser.web.base import WebParserBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class Web2Tables(WebParserBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table_output_dir = self.output_dir / "tables"
        self.table_output_dir.mkdir(parents=True, exist_ok=True)

    def extract2tables(self):
        """
        Extract the HTML file to tables and save it to the output directory

        """

        with open(f"{self.output_dir}/index.html", "r") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")
        for i, table in enumerate(soup.find_all("table")):
            rows = []
            for row in table.find_all("tr"):
                cells = [
                    cell.get_text(strip=True) for cell in row.find_all(["th", "td"])
                ]
                rows.append(cells)
            df = pd.DataFrame(rows[1:], columns=rows[0])  # Assuming first row is header
            csv_filename = f"{self.output_dir}/tables/{i}.csv"
            df.to_csv(csv_filename, index=False)
            logger.info(f"Extracted the HTML file from {self.url} to tables")
