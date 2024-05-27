"""
This module will require LLM support to clean and transform the unstructured data into structured data


"""

import os

import openai


def confirm_openai_api_key():
    """
    Confirm the OpenAI API key is set
    """
    if "OPENAI_API_KEY" not in os.environ:
        raise ValueError("OpenAI API key is not set")
    openai.api_key = os.getenv("OPENAI_API_KEY")


confirm_openai_api_key()
