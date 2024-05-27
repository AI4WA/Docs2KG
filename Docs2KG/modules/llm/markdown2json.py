import json
from pathlib import Path

import pandas as pd
from openai import OpenAI

from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)


class LLMMarkdown2Json:
    def __init__(self, markdown_file: Path):
        self.markdown_file = markdown_file
        if self.markdown_file.suffix != ".csv":
            raise ValueError("Only support csv")
        self.json_csv_file = markdown_file.with_suffix(".json.csv")
        self.client = OpenAI()

    def extract2json(self):
        df = pd.read_csv(self.markdown_file)
        df["json"] = df["text"].apply(self.openai_llm)
        df.to_csv(self.json_csv_file, index=False)

    def openai_layout_structure_json(self, markdown):
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
            markdown:

        Returns:

        """
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
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
        logger.info(content)
        return content
