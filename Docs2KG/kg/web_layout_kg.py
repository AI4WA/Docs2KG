import json
from copy import deepcopy
from pathlib import Path
from urllib.parse import quote, urlparse
from uuid import uuid4

import pandas as pd
import requests
from bs4 import BeautifulSoup

from Docs2KG.utils.constants import DATA_INPUT_DIR, DATA_OUTPUT_DIR
from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


"""
TODO:

- Try to extract the image and file captions
"""


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
        # extract the domain from the url, if it is http://example.com/sss, then the domain is https://example.com
        self.domain = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

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

        # image and table output directories
        self.image_output_dir = self.output_dir / "images"
        self.image_output_dir.mkdir(parents=True, exist_ok=True)
        self.table_output_dir = self.output_dir / "tables"
        self.table_output_dir.mkdir(parents=True, exist_ok=True)

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
        # FIXME: still not working properly
        node = {
            "uuid": str(uuid4()),
            "children": [],
        }

        for child in soup.children:
            if child.name is not None and soup.name != "table":
                child_node = self.extract_kg(child)
                node["children"].append(child_node)
        # content should be text if exists, if not, leave ""
        content = str(soup.text) if soup.text is not None else ""
        content = content.strip()
        logger.info(content)
        logger.info(soup.name)
        # if there is no parent, then it is the root node, which we call it document
        node_type = str(soup.name) if soup.name is not None else "text"
        if "document" in node_type:
            node_type = "document"

        node["node_type"] = node_type
        soup_attr = soup.attrs
        copied_soup = deepcopy(soup_attr)
        for key in copied_soup.keys():
            if "-" in key:
                soup_attr[key.replace("-", "_")] = copied_soup[key]
                del soup_attr[key]
            if "$" in key or ":" in key:
                del soup_attr[key]
        node["node_properties"] = {"content": content, **soup_attr}
        # if it is an image tag, then extract the image and save it to the output directory
        if soup.name == "img":
            img_url = soup.get("src")
            if not img_url.startswith("http"):
                img_url = self.domain + img_url
            img_data = requests.get(img_url).content
            img_name = img_url.split("/")[-1]
            logger.info("image_url")
            logger.info(img_url)
            if "?" in img_name:
                img_name = img_name.split("?")[0]
            with open(f"{self.output_dir}/images/{img_name}", "wb") as f:
                f.write(img_data)
            logger.info(f"Extracted the HTML file from {self.url} to images")
            node["node_properties"]["img_path"] = f"{self.output_dir}/images/{img_name}"
        # if it is a table tag, then extract the table and save it to the output directory
        if soup.name == "table":
            rows = []
            for row in soup.find_all("tr"):
                cells = [
                    cell.get_text(strip=True) for cell in row.find_all(["th", "td"])
                ]
                rows.append(cells)
            df = pd.DataFrame(rows[1:], columns=rows[0])  # Assuming first row is header
            csv_filename = f"{self.output_dir}/tables/{node['uuid']}.csv"
            df.to_csv(csv_filename, index=False)
            logger.info(f"Extracted the HTML file from {self.url} to tables")
            node["node_properties"]["table_path"] = csv_filename
        # remove the node from soup after extracting the image and table
        soup.extract()
        return node

    def export_kg(self) -> None:
        """
        Export the knowledge graph to json file
        """
        with open(self.kg_folder / "layout_kg.json", "w") as f:
            json.dump(self.kg_json, f, indent=2)
