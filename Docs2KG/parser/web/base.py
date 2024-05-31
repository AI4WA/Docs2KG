from pathlib import Path
from urllib.parse import quote

import requests

from Docs2KG.utils.constants import DATA_INPUT_DIR, DATA_OUTPUT_DIR
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class WebParserBase:
    def __init__(
        self, url: str, output_dir: Path = None, input_dir: Path = None
    ) -> None:
        """
        Initialize the WebParserBase class

        Args:
            url (str): URL to download the HTML files
            output_dir (Path): Path to the output directory where the converted files will be saved
            input_dir (Path): Path to the input directory where the html files will be downloaded
        """
        self.url = url
        self.output_dir = output_dir
        self.input_dir = input_dir
        self.quoted_url = quote(url, "")
        if self.output_dir is None:
            self.output_dir = DATA_OUTPUT_DIR / self.quoted_url
            self.output_dir.mkdir(parents=True, exist_ok=True)

        self.download_html_file()

    def download_html_file(self):
        """
        Download the html file from the url and save it to the input directory

        """
        response = requests.get(self.url)
        if response.status_code == 200:
            with open(f"{DATA_INPUT_DIR}/index.html", "wb") as f:
                f.write(response.content)
            logger.info(f"Downloaded the HTML file from {self.url}")
        else:
            logger.error(f"Failed to download the HTML file from {self.url}")
