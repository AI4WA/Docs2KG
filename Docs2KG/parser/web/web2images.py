from urllib.parse import quote, unquote, urljoin

import requests
from bs4 import BeautifulSoup

from Docs2KG.parser.web.base import WebParserBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class Web2Images(WebParserBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_output_dir = self.output_dir / "images"
        self.image_output_dir.mkdir(parents=True, exist_ok=True)

    def extract2images(self):
        """
        Extract the HTML file to images and save it to the output directory

        """
        url = unquote(self.url)
        with open(f"{self.output_dir}/index.html", "r") as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, "html.parser")
        for imgtag in soup.find_all("img"):
            img_url = imgtag.get("src")
            if not img_url.startswith("http"):
                img_url = urljoin(url, img_url)
            img_data = requests.get(img_url).content
            img_name = quote(imgtag["src"], "")

            with open(f"{self.output_dir}/images/{img_name}", "wb") as f:
                f.write(img_data)
            logger.info(f"Extracted the HTML file from {url} to images")
