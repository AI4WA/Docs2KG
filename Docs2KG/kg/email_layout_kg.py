import json
from copy import deepcopy
from pathlib import Path
from uuid import uuid4

import pandas as pd
import requests
from bs4 import BeautifulSoup

from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


"""
TODO:

- Try to extract the image and file captions
"""


class EmailLayoutKG:
    def __init__(self, output_dir: Path = None) -> None:
        """
        Initialize the WebParserBase class

        Args:
            output_dir (Path): Path to the output directory where the converted files will be saved

        """

        self.output_dir = output_dir

        self.kg_json = {}
        self.kg_folder = self.output_dir / "kg"
        self.kg_folder.mkdir(parents=True, exist_ok=True)

        # image and table output directories
        self.image_output_dir = self.output_dir / "images"
        self.image_output_dir.mkdir(parents=True, exist_ok=True)
        # attachment output directories
        self.attachment_output_dir = self.output_dir / "attachments"
        self.attachment_output_dir.mkdir(parents=True, exist_ok=True)

        self.images_df = pd.read_csv(f"{self.image_output_dir}/images.csv")
        self.attachments_df = pd.read_csv(
            f"{self.attachment_output_dir}/attachments.csv"
        )

    def create_kg(self):
        """
        Create the knowledge graph from the HTML file

        """
        with open(f"{self.output_dir}/email.html", "r") as f:
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
            node_type = "email"
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

            if img_url.startswith("cid:"):
                image_cid = img_url.split(":")[1]
                logger.info(image_cid)
                image_file_path = self.images_df[
                    self.images_df["cid"] == f"<{image_cid}>"
                ]["path"].values[0]
                logger.info(image_file_path)
                node["node_properties"]["img_path"] = image_file_path
            else:
                img_data = requests.get(img_url).content
                img_name = img_url.split("/")[-1]
                logger.info("image_url")
                logger.info(img_url)
                if "?" in img_name:
                    img_name = img_name.split("?")[0]
                with open(f"{self.output_dir}/images/{img_name}", "wb") as f:
                    f.write(img_data)
                logger.info(f"Extracted the HTML file from {img_url} to images")
                node["node_properties"][
                    "img_path"
                ] = f"{self.output_dir}/images/{img_name}"
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
            logger.info("Extracted the HTML file from to tables")
            node["node_properties"]["table_path"] = csv_filename
        # remove the node from soup after extracting the image and table
        soup.extract()

        if node_type == "email":
            # also add the metadata to the node properties
            with open(f"{self.output_dir}/metadata.json", "r") as f:
                metadata = json.load(f)
            node["node_properties"] = {**node["node_properties"], **metadata}

            # add all the attachments to children
            for _, attachment in self.attachments_df.iterrows():
                attachment_node = {
                    "uuid": str(uuid4()),
                    "node_type": "attachment",
                    "node_properties": attachment.to_dict(),
                    "children": [],
                }
                node["children"].append(attachment_node)
        return node

    def export_kg(self) -> None:
        """
        Export the knowledge graph to json file
        """
        with open(self.kg_folder / "layout_kg.json", "w") as f:
            json.dump(self.kg_json, f, indent=2)
