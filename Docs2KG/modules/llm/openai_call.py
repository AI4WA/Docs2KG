from typing import List, Tuple

from openai import OpenAI

from Docs2KG.utils.get_logger import get_logger
from Docs2KG.utils.llm.track_usage import track_usage

logger = get_logger(__name__)
client = OpenAI()


def openai_call(
    messages: List[dict], llm_model_name: str = "gpt-3.5-turbo"
) -> Tuple[str, float]:
    """
    Call the OpenAI API to get the response
    Args:
        messages (List[dict]): The messages to send to the OpenAI API
        llm_model_name (str): The name of the LLM model


    Returns:
        response_json_str (str): The response from the OpenAI API
        cost (float): The cost of the response
    """
    result_json_str = ""
    cost = 0
    while True:
        response = client.chat.completions.create(
            model=llm_model_name,
            response_format={"type": "json_object"},
            messages=messages,
            temperature=0.0,
        )
        logger.debug(response)
        content = response.choices[0].message.content
        logger.debug(content)
        result_json_str += content
        cost += track_usage(response)
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

    return result_json_str, cost
