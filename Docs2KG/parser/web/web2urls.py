import pandas as pd
from bs4 import BeautifulSoup

from Docs2KG.parser.web.base import WebParserBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class Web2URLs(WebParserBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table_output_dir = self.output_dir / "urls"
        self.table_output_dir.mkdir(parents=True, exist_ok=True)

    def extract2tables(self):
        """
        Extract the HTML file to tables and save it to the output directory

        """

        with open(f"{self.output_dir}/index.html", "r") as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, "html.parser")
        # find all urls and save them to a csv file
        urls = []
        for a in soup.find_all("a"):
            urls.append(a.get("href"))
        df = pd.DataFrame(urls, columns=["URL"])
        csv_filename = f"{self.output_dir}/urls/urls.csv"
        df.to_csv(csv_filename, index=False)
