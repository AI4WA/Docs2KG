from pathlib import Path
from typing import List

import pandas as pd
from openai import OpenAI
from tqdm import tqdm

from Docs2KG.utils.get_logger import get_logger
from Docs2KG.utils.llm.track_usage import track_usage

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
        self.client = OpenAI()
        self.cost = 0

    def extract2json(self):
        if self.json_csv_file.exists():
            logger.info(f"{self.json_csv_file} already exists")
            return
        current_cost = self.cost
        df = pd.read_csv(self.markdown_file)

        for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Layout JSON"):
            df.at[index, "layout_json"] = self.openai_layout_json(row["text"])
        for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Content JSON"):
            df.at[index, "content_json"] = self.openai_content_json(row["text"])

        df.to_csv(self.json_csv_file, index=False)
        logger.info(f"Cost: {self.cost - current_cost}")

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
                    
        The markdown given to you will have some noise/not meaningful characters or information, you need to think about cleaning
        the markdown into a cleaned version.
        
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
        return self.openai_call(messages)

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
        return self.openai_call(messages)

    def openai_call(self, messages: List[dict]) -> str:
        """
        Call the OpenAI API to get the response
        Args:
            messages (List[dict]): The messages to send to the OpenAI API


        Returns:
            response_json_str (str): The response from the OpenAI API
        """
        result_json_str = ""
        while True:
            response = self.client.chat.completions.create(
                model=self.llm_model_name,
                response_format={"type": "json_object"},
                messages=messages,
            )
            logger.debug(response)
            content = response.choices[0].message.content
            logger.debug(content)
            result_json_str += content
            self.cost += track_usage(response)
            # if finish_reason is length, then it is not complete
            logger.debug(response.choices[0].finish_reason)
            if response.choices[0].finish_reason != "length":
                break
            else:
                messages.append(
                    {
                        "role": "assistant",
                        "content": content,
                    }
                )
                messages.append(
                    {
                        "role": "user",
                        "content": "Continue the response",
                    }
                )

        return result_json_str
