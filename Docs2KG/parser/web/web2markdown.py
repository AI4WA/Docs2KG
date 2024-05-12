from urllib.parse import quote

import requests
from bs4 import BeautifulSoup
from markdownify import MarkdownConverter
from markdownify import markdownify as md

from Docs2KG.parser.web.base import WebParserBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)

class Web2Markdown(WebParserBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.markdown_output_dir = self.output_dir / "markdowns"
        self.markdown_output_dir.mkdir(parents=True, exist_ok=True)

    def convert2markdown(self, quoted_url):
        """
        Convert the HTML file to markdown and save it to the output directory
        """
        with open(f'{self.input_dir}/{quoted_url}.html', 'r') as f:
            html_content = f.read()
        markdown_file = md(html_content)
        with open(f'{self.markdown_output_dir}/{quoted_url}.md', 'w') as f:
            f.write(str(markdown_file))

    def batch_convert2markdown(self):
        """
        Batch convert html files to markdown
        """
        for quoted_url in self.quoted_urls:
            self.convert2markdown(quoted_url)
            logger.info(f"Converted the HTML file from {quoted_url} to markdown")
        logger.info("All HTML files have been converted to markdown files!")