import json
from pathlib import Path
from typing import List

import pandas as pd
from tqdm import tqdm

from Docs2KG.modules.llm.openai_call import openai_call
from Docs2KG.utils.get_logger import get_logger

tqdm.pandas()

logger = get_logger(__name__)


class Sheet2Metadata:
    def __init__(self, markdown_file: Path, llm_model_name: str = "gpt-3.5-turbo-0125"):
        """
        1. Extract the descriptive part of the markdown
        2. Summary the markdown

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

    def extract_metadata(self):
        if self.json_csv_file.exists():
            logger.info(f"{self.json_csv_file} already exists")
            return
        logger.info(self.markdown_file)
        current_cost = self.cost
        df = pd.read_csv(self.markdown_file)

        for index, row in tqdm(
            df.iterrows(), total=df.shape[0], desc="Summary and Description Extraction"
        ):
            try:
                summary, desc = self.openai_sheet_handler(row["text"])
                logger.info(summary)
                logger.info(desc)
                # if it is list, then we will join them
                if isinstance(summary, list):
                    summary = " ".join(summary)
                if isinstance(desc, list):
                    desc = " ".join(desc)
                try:
                    df.loc[index, "summary"] = summary
                    df.loc[index, "desc"] = desc
                except Exception as e:
                    logger.error(e)
                    df.loc[index, "summary"] = str(summary)
                    df.loc[index, "desc"] = str(desc)
            except Exception as e:
                logger.error(e)
                df.loc[index, "summary"] = str()
                df.loc[index, "desc"] = ""
                logger.error(f"Error at index {index}")

        df.to_csv(self.json_csv_file, index=False)
        logger.info(f"Cost: {self.cost - current_cost}")

    def openai_sheet_handler(self, markdown: str):
        """
        1. Use OpenAI to exclude the numerical part of the markdown, only keep the descriptive part
        2. Summarize the markdown

        Args:
            markdown:

        Returns:

        """
        messages = [
            {
                "role": "system",
                "content": """
                    You are a helpful assistant, help us clean and understand the excel data
                    You will need to first summary the markdwon content, it is normally some descriptive text with
                    Table information.
                    """,
            },
            {
                "role": "user",
                "content": f"""
                            We will need you to do two things:
                            1. Summarize the following markdown content into a description about the data:
                                - What the data is about
                                - What's the main point of the data
                            2. Exclude the numerical part of the markdown, only keep the descriptive part.

                            The markdown content is: \n\n{markdown}

                            Return in JSON format with key "summary" and "desc"
                            """,
            },
        ]
        try:
            content = self.llm_openai_call(messages)
            content = json.loads(content)
            return content["summary"], content["desc"]
        except Exception as e:
            logger.error(e)
            return "", ""

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
        logger.debug(result_json_str)
        logger.debug(f"Cost: {self.cost}")
        return result_json_str
