import json
from pathlib import Path
from typing import List, Optional

import pandas as pd
from tqdm import tqdm

from Docs2KG.modules.llm.openai_call import openai_call
from Docs2KG.utils.get_logger import get_logger

tqdm.pandas()

logger = get_logger(__name__)


class LLMMarkdown2Json:
    def __init__(self, markdown_file: Path, llm_model_name: str = "gpt-3.5-turbo-0125"):
        """
        Convert markdown to json using OpenAI LLM

        There are two types of JSON (Structured format)

        - JSON for layout structure
        - JSON for content structure

        It will be interesting to compare and see the difference between the two

        Args:
            markdown_file (Path): The path to the markdown file
            llm_model_name (str): The OpenAI LLM model name
        """
        self.markdown_file = markdown_file
        if self.markdown_file.suffix != ".csv":
            raise ValueError("Only support csv")
        self.json_csv_file = markdown_file.with_suffix(".json.csv")
        self.llm_model_name = llm_model_name
        self.cost = 0

    def clean_markdown(self) -> Optional[str]:
        """
        Prompt will give the LLM Markdown text

        Ask it clean it, and then get the Markdown into proper format

        Returns:
            str: The cleaned Markdown text
        """
        current_cost = self.cost
        cleaned_markdown_csv = self.markdown_file.with_suffix(".cleaned.csv")
        if cleaned_markdown_csv.exists():
            logger.info(f"{cleaned_markdown_csv} already exists")
            return
        df = pd.read_csv(self.markdown_file)
        for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Layout JSON"):
            cleaned_markdown = self.openai_clean_markdown(row["text"])
            df.at[index, "text"] = cleaned_markdown
        df.to_csv(cleaned_markdown_csv, index=False)
        logger.info(f"Cost: {self.cost - current_cost}")

    def extract2json(self):
        if self.json_csv_file.exists():
            logger.info(f"{self.json_csv_file} already exists")
            return
        logger.info(self.markdown_file)
        current_cost = self.cost
        df = pd.read_csv(self.markdown_file)

        for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Layout JSON"):
            df.at[index, "layout_json"] = self.openai_layout_json(row["text"])
        for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Content JSON"):
            df.at[index, "content_json"] = self.openai_content_json(row["text"])

        df.to_csv(self.json_csv_file, index=False)
        logger.info(f"Cost: {self.cost - current_cost}")

    def openai_clean_markdown(self, markdown):
        """
        Use OpenAI LLM to clean the markdown

        The markdown will be cleaned using the OpenAI LLM

        Args:
            markdown (str): The Markdown text

        Returns:
            str: The cleaned Markdown text
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful assistant to clean the markdown text.""",
                },
                {
                    "role": "user",
                    "content": f"""
                                You task is to clean the markdown.

                                Steps include

                                - Remove the content which is not meaningful, such as a single I character, etc
                                - Do not need to keep special characters, such as `#`, `*`, etc, only keep
                                    meaningful content
                                - Make sure the markdown is fit with the markdown format
                                - Only do remove for the noise characters, do not change any content

                                Output should be a cleaned markdown text, which in str format

                                It will stay in the response in json format
                                with a key "cleaned_markdown"

                                Clean the following markdown text:\n\n{markdown}
                                """,
                },
            ]
            markdown_json = self.llm_openai_call(messages)
            logger.debug(markdown_json)
            return json.loads(markdown_json).get("cleaned_markdown", None)
        except Exception as e:
            logger.exception(e)
            return None

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
        messages = [
            {
                "role": "system",
                "content": """You are a helpful assistant to convert markdown to JSON format.

        The markdown given to you will have some noise/not meaningful characters or information, you need to think
        about cleaning the markdown into a cleaned version.

        Then convert the markdown to json

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

        Keep the meaningful hierarchy information within markdown via the html h1/h2/... tags
        Get them proper in json format.

        If it is a table, leave it as
        {
            "tag": "table",
            "content": "",
            "children": []
        }
        Content should the full content of the table, do not decompose further into tr/td/th, etc

        One example can be
        {
            "tag": "table",
            "content": ",header,header,
                        value,value....
                        ",
            "children": []
        }

        """,
            },
            {
                "role": "user",
                "content": f"Convert the following markdown to JSON format:\n\n{markdown}",
            },
        ]
        return self.llm_openai_call(messages)

    def openai_content_json(self, markdown: str):
        """
        Use OpenAI LLM to convert markdown to json

        The markdown will be converted to json using the OpenAI LLM
        Main focus here is to convert the content to json
        Args:
            markdown:

        Returns:

        """
        messages = [
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
        ]
        return self.llm_openai_call(messages)

    def llm_openai_call(self, messages: List[dict]) -> str:
        """
        Call the OpenAI API to get the response
        Args:
            messages (List[dict]): The messages to send to the OpenAI API


        Returns:
            response_json_str (str): The response from the OpenAI API
        """
        result_json_str, cost = openai_call(messages, self.llm_model_name)
        self.cost += cost
        return result_json_str
