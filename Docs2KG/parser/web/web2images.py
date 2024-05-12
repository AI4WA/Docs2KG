from Docs2KG.parser.web.base import WebParserBase
from Docs2KG.utils.get_logger import get_logger
from bs4 import BeautifulSoup
import requests
from urllib.parse import quote, unquote, urljoin

logger = get_logger(__name__)

class Web2Images(WebParserBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_output_dir = self.output_dir / "images"
        self.image_output_dir.mkdir(parents=True, exist_ok=True)

    def extract2images(self, quoted_url):
        """
        Extract the HTML file to images and save it to the output directory
        """
        url = unquote(quoted_url)
        html_img_dir = self.image_output_dir / quoted_url
        html_img_dir.mkdir(parents=True, exist_ok=True)
        with open(f'{self.input_dir}/{quoted_url}.html', 'r') as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, 'html.parser')
        for imgtag in soup.find_all('img'):
            img_url = imgtag.get('src')
            if not img_url.startswith('http'):
                img_url = urljoin(url, img_url)
            img_data = requests.get(img_url).content
            img_name = quote(imgtag['src'], '')

            with open(f'{html_img_dir}/{img_name}', 'wb') as f:
                f.write(img_data)
            logger.info(f"Extracted the HTML file from {url} to images")

    def batch_extract2images(self):
        """
        Batch extract html files to images
        """
        for quoted_url in self.quoted_urls:
            self.extract2images(quoted_url)
            logger.info(f"Extracted the HTML file from {unquote(quoted_url)} to images")
        logger.info("All HTML files have been extracted to images!")