from pathlib import Path


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
        self.markdown_file = markdown_file
        self.json_file = markdown_file.with_suffix(".json")

    def extract2json(self):
        """
        Extract the markdown file to JSON and save it to the output directory
        """
        with open(self.markdown_file, "r") as f:
            markdown_content = f.read()
