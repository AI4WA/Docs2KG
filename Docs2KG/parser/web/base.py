from pathlib import Path
from typing import List
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from Docs2KG.utils.constants import DATA_INPUT_DIR, DATA_OUTPUT_DIR
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)

class WebParserBase:
    def __init__(self, urls:List[str], output_dir: Path = None, input_dir: Path = None) -> None:
        """
        Initialize the WebParserBase class
        :param urls: List of URLs to download the HTML files
        :param output_dir: Path to the output directory where the converted files will be saved
        :param input_dir: Path to the input directory where the html files will be downloaded
        """
        self.urls = urls
        self.output_dir = output_dir
        self.input_dir = input_dir
        self.quoted_urls = [quote(url, '') for url in urls]
        if self.output_dir is None or self.input_dir is None:
            web_output_folder = DATA_OUTPUT_DIR / "web"
            web_input_folder = DATA_INPUT_DIR / "web"
            web_output_folder.mkdir(parents=True, exist_ok=True)
            web_input_folder.mkdir(parents=True, exist_ok=True)
            self.output_dir = web_output_folder
            self.input_dir = web_input_folder

    def download_html_file(self, url):
        """
        Download the html file from the url and save it to the input directory
        """
        response = requests.get(url)
        if response.status_code == 200:
            html_file = quote(url, '')
            soup = BeautifulSoup(response.content, 'html.parser')
            # save the HTML content to a file
            with open(f'{self.input_dir}/{html_file}.html', 'w') as f:
                f.write(str(soup))
            logger.info(f"Downloaded the HTML file from {url}")
        else:
            logger.error(f"Failed to download the HTML file from {url}")

    def batch_download(self):
        """
        Batch download the HTML files from the URLs
        """
        for url in self.urls:
            self.download_html_file(url)
        logger.info("All HTML files have been downloaded!")
