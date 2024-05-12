from Docs2KG.parser.web.base import WebParserBase
from Docs2KG.utils.get_logger import get_logger
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote, unquote
import csv
import pandas as pd

logger = get_logger(__name__)

class Web2Tables(WebParserBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table_output_dir = self.output_dir / "tables"
        self.table_output_dir.mkdir(parents=True, exist_ok=True)

    def extract2tables(self, quoted_url):
        """
        Extract the HTML file to tables and save it to the output directory
        """
        html_tab_dir = self.table_output_dir / quoted_url
        html_tab_dir.mkdir(parents=True, exist_ok=True)

        with open(f'{self.input_dir}/{quoted_url}.html', 'r') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')
        for i, table in enumerate(soup.find_all('table')):
            rows = []
            for row in table.find_all('tr'):
                cells = [cell.get_text(strip=True) for cell in row.find_all(['th', 'td'])]
                rows.append(cells)
            df = pd.DataFrame(rows[1:], columns=rows[0])  # Assuming first row is header
            csv_filename = f'{html_tab_dir}/{i}.csv'
            df.to_csv(csv_filename, index=False)
            logger.info(f"Extracted the HTML file from {unquote(quoted_url)} to tables")

    def batch_extract2tables(self):
        """
        Batch extract html files to tables
        """
        for quoted_url in self.quoted_urls:
            self.extract2tables(quoted_url)
            logger.info(f"Extracted the HTML file from {unquote(quoted_url)} to tables")
        logger.info("All HTML files have been extracted to tables!")