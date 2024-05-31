from markdownify import markdownify as md

from Docs2KG.parser.web.base import WebParserBase
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class Web2Markdown(WebParserBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.markdown_output_dir = self.output_dir / "markdowns"
        self.markdown_output_dir.mkdir(parents=True, exist_ok=True)

    def convert2markdown(self):
        """
        Convert the HTML file to markdown and save it to the output directory

        """
        with open(f"{self.output_dir}/index.html", "r") as f:
            html_content = f.read()
        markdown_file = md(html_content)
        with open(f"{self.markdown_output_dir}/content.md", "w") as f:
            f.write(str(markdown_file))
