import json
from pathlib import Path

import pandas as pd

from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class Markdown2JSON:
    """
    We want to make the semi-structured data into structured format, which is JSON format.

    If it is a well-formatted markdown file, we should be able to get it into JSON format via programmatic methods.

    However, if it is not a well-formatted markdown file, for example

    ```
    # Title

    ## Subtitle

    - Item 1


    ##### I

    Prosperity Resources - Perth office

    ##### I

    ##### I
    ##### I

    ##### I
    ##### I

    ##### I
    ##### I

    ##### I
    ```

    We will need to use NLP techniques to extract the structured information from the markdown file, or
    we need the help from LLMs to generate the structured information from the markdown file.
    """

    def __init__(self, markdown_file: Path):
        """
        Initialize the markdown file and the output JSON file
        Args:
            markdown_file (Path): The markdown file to be converted to JSON
        """
        # if it is ending with .md, then it is a markdown file
        # if it is ending with .csv, then it is a csv file
        self.markdown_file = markdown_file
        self.json_csv_file = markdown_file.with_suffix(".json.csv")

    @staticmethod
    def markdown_to_json(markdown):
        lines = markdown.split("\n")
        json_data = {"tag": "root", "content": "", "children": []}

        stack = [json_data]

        for line in lines:
            if line.startswith("#"):
                level = line.count("#")
                new_tag = "h" + str(level)
                new_content = line.lstrip("# ").strip()

                # Find the correct parent for the current tag
                while len(stack) > level:
                    stack.pop()

                parent = stack[-1]
                new_node = {"tag": new_tag, "content": new_content, "children": []}
                parent["children"].append(new_node)
                stack.append(new_node)
            elif line.strip() != "":
                current_node = stack[-1]
                current_node["children"].append(
                    {"tag": "p", "content": line.strip(), "children": []}
                )
        return json_data

    def extract2json_from_csv(self) -> pd.DataFrame:
        """
        Extract the csv file to JSON and save it to the output directory

        Returns:
            json_csv (pd.DataFrame): The DataFrame containing the JSON content
        """
        df = pd.read_csv(self.markdown_file)
        # loop the df
        for index, row in df.iterrows():
            json_content = self.markdown_to_json(row["text"])
            logger.debug(json_content)
            df.at[index, "json"] = json.dumps(json_content)
        df.to_csv(self.json_csv_file, index=False)
        return df
