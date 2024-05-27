from pathlib import Path

import pandas as pd
from openai import OpenAI
from tqdm import tqdm

from Docs2KG.utils.get_logger import get_logger

tqdm.pandas()

logger = get_logger(__name__)


class LLMMarkdown2Json:
    def __init__(self, markdown_file: Path,
                 llm_model_name: str = "gpt-3.5-turbo"):
        """
        Convert markdown to json using OpenAI LLM

        There are two types of JSON (Structured format)

        - JSON for layout structure
        - JSON for content structure

        It will be interesting to compare and see the difference between the two

        Args:
            markdown_file (Path): The path to the markdown file
        """
        self.markdown_file = markdown_file
        if self.markdown_file.suffix != ".csv":
            raise ValueError("Only support csv")
        self.json_csv_file = markdown_file.with_suffix(".json.csv")
        self.llm_model_name = llm_model_name
        self.client = OpenAI()

    def extract2json(self):
        if self.json_csv_file.exists():
            logger.info(f"{self.json_csv_file} already exists")
            return
        df = pd.read_csv(self.markdown_file)
        # show progress bar
        df["layout_json"] = df["text"].progress_apply(
            self.openai_layout_json
        )
        tqdm.pandas(
            desc="Layout JSON"
        )
        df["content_json"] = df["text"].progress_apply(
            self.openai_content_json, desc="Content JSON"
        )
        tqdm.pandas(
            desc="Content JSON"
        )
        df.to_csv(self.json_csv_file, index=False)

    def openai_layout_json(self, markdown):
        """
        Use OpenAI LLM to convert markdown to json

        The markdown will be converted to json using the OpenAI LLM

        Output format should be like

        Examples:
            {
            "tag": "root",
            "content": {title},
            "children": [
                {
                "tag": "h1",
                "content": "This is the header 1",
                "children": [
                    {
                    "tag": "h2",
                    "content": "This is the header 2",
                    "children": [
                        ....
                        {
                        "tag": "p",
                        "content": "This is the paragraph",
                        "children": []
                        }
                    ]
                    }
                ]
                }
            ]
            }

        For Example:

        ```markdown
        # Title
        ## Subtitle
        ### Subtitle 2
        - Item 1
        - Item 2
        - Item 3

        ## Subtitle 3
        - Item 1
        - Item 2

        This is a paragraph

        ## Subtitle 4
        - Item 1
        - Item 2
        ```

        Should output as

        ```json
        {
        "tag": "h1",
        "content": "Title",
        "children": [
            {
                "tag": "h2",
                "content": "Subtitle",
                "children": [
                    {
                        "tag": "h3",
                        "content": "Subtitle 2",
                        "children": [
                            {
                                "tag": "li",
                                "content": "Item 1",
                                "children": []
                            },
                            {
                                "tag": "li",
                                "content": "Item 2",
                                "children": []
                            },
                            {
                                "tag": "li",
                                "content": "Item 3",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            {
                "tag": "h2",
                "content": "Subtitle 3",
                "children": [
                    {
                        "tag": "li",
                        "content": "Item 1",
                        "children": []
                    },
                    {
                        "tag": "li",
                        "content": "Item 2",
                        "children": []
                    }
                ]
            },
            {
                "tag": "p",
                "content": "This is a paragraph",
                "children": []
            },
            {
                "tag": "h2",
                "content": "Subtitle 4",
                "children": [
                    {
                        "tag": "li",
                        "content": "Item 1",
                        "children": []
                    },
                    {
                        "tag": "li",
                        "content": "Item 2",
                        "children": []
                    }
                ]
            }
        ]
        }
        ```

        Args:
            markdown (str): The Markdown text

        Returns:

        """
        response = self.client.chat.completions.create(
            model=self.llm_model_name,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful assistant to convert markdown to JSON format.
        For Example:

        ```markdown
        # Title
        ## Subtitle
        ### Subtitle 2
        - Item 1
        - Item 2
        - Item 3

        ## Subtitle 3
        - Item 1
        - Item 2

        This is a paragraph

        ## Subtitle 4
        - Item 1
        - Item 2
        ```

        Should output as

        ```json
        {
        "tag": "h1",
        "content": "Title",
        "children": [
            {
                "tag": "h2",
                "content": "Subtitle",
                "children": [
                    {
                        "tag": "h3",
                        "content": "Subtitle 2",
                        "children": [
                            {
                                "tag": "li",
                                "content": "Item 1",
                                "children": []
                            },
                            {
                                "tag": "li",
                                "content": "Item 2",
                                "children": []
                            },
                            {
                                "tag": "li",
                                "content": "Item 3",
                                "children": []
                            }
                        ]
                    }
                ]
            },
            {
                "tag": "h2",
                "content": "Subtitle 3",
                "children": [
                    {
                        "tag": "li",
                        "content": "Item 1",
                        "children": []
                    },
                    {
                        "tag": "li",
                        "content": "Item 2",
                        "children": []
                    },
                    {
                        "tag": "p",
                        "content": "This is a paragraph",
                        "children": []
                    },
                ]
            },
            {
                "tag": "h2",
                "content": "Subtitle 4",
                "children": [
                    {
                        "tag": "li",
                        "content": "Item 1",
                        "children": []
                    },
                    {
                        "tag": "li",
                        "content": "Item 2",
                        "children": []
                    }
                ]
            }
        ]
        }
        ```
        
        tag will be from the html convention like h1, h2, h3, p, li, etc.
        """,
                },
                {
                    "role": "user",
                    "content": f"Convert the following markdown to JSON format:\n\n{markdown}",
                },
            ],
        )
        logger.debug(response)
        content = response.choices[0].message.content
        logger.debug(content)
        return content

    def openai_content_json(self, markdown: str):
        """
        Use OpenAI LLM to convert markdown to json

        The markdown will be converted to json using the OpenAI LLM
        Main focus here is to convert the content to json
        Args:
            markdown:

        Returns:

        """
        response = self.client.chat.completions.create(
            model=self.llm_model_name,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are a helpful assistant to convert markdown to JSON format.
                    You will be focusing on extracting meaningful key-value pairs from the markdown text.
                    """,
                },
                {
                    "role": "user",
                    "content": f"Convert the following markdown to JSON format:\n\n{markdown}",
                },
            ],
        )
        logger.debug(response)
        content = response.choices[0].message.content
        logger.debug(content)
        return content
