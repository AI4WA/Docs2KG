import json
import uuid
from typing import Any, Dict, List

import markdown
from bs4 import BeautifulSoup

from Docs2KG.kg_construction.base import KGConstructionBase
from Docs2KG.utils.config import PROJECT_CONFIG


class LayoutKGConstruction(KGConstructionBase):
    """
    Constructs a layout knowledge graph from markdown documents.
    The output is a JSON file for each document containing layout elements.
    """

    def __init__(self, project_id: str):
        super().__init__(project_id)
        self.md = markdown.Markdown(extensions=["tables", "fenced_code"])

    def _parse_html_element(self, element: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Parse an HTML element and extract layout information.

        Args:
            element: BeautifulSoup element from parsed markdown

        Returns:
            list: List of element information including id, text, and label
        """
        elements = []

        # Skip empty elements
        if not element.text.strip():
            return elements

        # Generate element ID
        element_id = f"p_{str(uuid.uuid4())}"

        # Map HTML tags to layout labels
        tag_to_label = {
            "h1": "H1",
            "h2": "H2",
            "h3": "H3",
            "h4": "H4",
            "h5": "H5",
            "h6": "H6",
            "p": "P",
            "li": "LI",
            "ol": "OL",
            "ul": "UL",
            "blockquote": "QUOTE",
            "pre": "CODE",
            "code": "CODE",
            "table": "TABLE",
            "tr": "TR",
            "td": "TD",
            "th": "TH",
        }

        # Get the element's tag name
        tag = element.name

        # If it's a recognized tag, create an element entry
        if tag in tag_to_label:
            elements.append(
                {
                    "id": element_id,
                    "text": element.get_text().strip(),
                    "label": tag_to_label[tag],
                    "entities": [],
                    "relations": [],
                }
            )

        # Recursively process child elements
        for child in element.children:
            if hasattr(child, "name") and child.name is not None:
                elements.extend(self._parse_html_element(child))

        return elements

    def _process_document(self, content: str, filename: str) -> Dict[str, Any]:
        """
        Process a single markdown document and extract its layout elements.

        Args:
            content: Content of the markdown file
            filename: Name of the document

        Returns:
            dict: Structured document information with layout elements
        """
        # Convert markdown to HTML
        html = self.md.convert(content)

        # Parse HTML
        soup = BeautifulSoup(html, "html.parser")

        # Extract elements
        elements = []
        for element in soup.find_all(recursive=False):
            elements.extend(self._parse_html_element(element))

        return {
            "filename": filename,
            "data": elements,
            "metadata": {
                "title": filename,
            },
        }

    def construct(self, docs: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Construct the layout knowledge graph from a list of documents.

        Args:
            docs: List of documents, where each document is a dict containing
                 'content' and 'filename' keys

        Returns:
            dict: Layout knowledge graph containing all processed documents
        """
        layout_kg = {}
        # output a layout schema json
        layout_schema = {
            "H1": ["H2", "P", "LI", "OL", "UL", "QUOTE", "CODE", "TABLE"],
            "H2": ["H3", "P", "LI", "OL", "UL", "QUOTE", "CODE", "TABLE"],
            "H3": ["H4", "P", "LI", "OL", "UL", "QUOTE", "CODE", "TABLE"],
            "H4": ["H5", "P", "LI", "OL", "UL", "QUOTE", "CODE", "TABLE"],
            "H5": ["H6", "P", "LI", "OL", "UL", "QUOTE", "CODE", "TABLE"],
            "H6": ["P", "LI", "OL", "UL", "QUOTE", "CODE", "TABLE"],
            "P": ["P", "LI", "OL", "UL", "QUOTE", "CODE", "TABLE"],
            "LI": ["LI", "OL", "UL", "P"],
            "OL": ["LI", "OL", "UL", "P"],
            "UL": ["LI", "OL", "UL", "P"],
            "QUOTE": ["P", "LI", "OL", "UL", "CODE"],
            "CODE": ["CODE"],
            "TABLE": ["TR"],
            "TR": ["TD", "TH"],
            "TD": ["P"],
            "TH": ["P"],
        }
        output_path = self.layout_folder / "schema.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(layout_schema, f, indent=2, ensure_ascii=False)

        for doc in docs:
            content = doc["content"]
            filename = doc["filename"]

            # Process the document
            doc_kg = self._process_document(content, filename)

            # Save individual document KG
            output_path = self.layout_folder / f"{filename}.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(doc_kg, f, indent=2, ensure_ascii=False)

            # Add to the complete KG
            layout_kg[filename] = doc_kg

        return layout_kg


if __name__ == "__main__":
    project_id = "wamex"
    md_files = (
        PROJECT_CONFIG.data.output_dir
        / "gsdRec_2024_08"
        / "PDFDocling"
        / "gsdRec_2024_08.md"
    )
    layout_kg_construction = LayoutKGConstruction(project_id)
    layout_kg_construction.construct(
        [{"content": md_files.read_text(), "filename": md_files.stem}]
    )
