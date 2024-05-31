from pathlib import Path
from urllib.parse import quote
from bs4 import BeautifulSoup
from uuid import uuid4
import requests
import json
from Docs2KG.utils.constants import DATA_INPUT_DIR, DATA_OUTPUT_DIR
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class WebLayoutKG:
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

        self.kg_json = {}
        self.kg_folder = self.output_dir / "kg"
        self.kg_folder.mkdir(parents=True, exist_ok=True)

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

    def create_kg(self):
        """
        Create the knowledge graph from the HTML file

        """
        with open(f"{DATA_INPUT_DIR}/index.html", "r") as f:
            html_content = f.read()
        soup = BeautifulSoup(html_content, "html.parser")
        """
        Loop and extract the whole soup into a tree
        Each node will have

        ```
        {
            "uuid": str,
            "node_type": str,
            "node_properties": {
                "content": str,
                // all other stuff
            },
            "children": List[Node]
        }
        ```
        """
        self.kg_json = self.extract_kg(soup)
        self.export_kg()

    def extract_kg(self, soup):
        """
        Extract the knowledge graph from the HTML file

        Args:
            soup (BeautifulSoup): Parsed HTML content

        Returns:
            dict: Knowledge graph in JSON format

        """
        # content should be text if exists, if not, leave ""
        content = "".join(soup.stripped_strings) if soup.stripped_strings else ""
        node = {
            "uuid": str(uuid4()),
            "node_type": soup.name if soup.name is not None else "text",
            "node_properties": {"content": content},
            "children": [],
        }
        for child in soup.children:
            if child.name is not None:
                child_node = self.extract_kg(child)
                node["children"].append(child_node)
        return node

    def export_kg(self) -> None:
        """
        Export the knowledge graph to json file
        """
        with open(self.kg_folder / "layout_kg.json", "w") as f:
            json.dump(self.kg_json, f, indent=2)
