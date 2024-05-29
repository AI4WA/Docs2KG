from openai.types.chat import ChatCompletion

from Docs2KG.utils.get_logger import get_logger

logger = get_logger(__name__)

OPENAI_MODEL_PRICE = {
    "gpt-3.5-turbo-0125": {"input_cost": 0.5, "output_cost": 1.5},
    "gpt-4o": {"input_cost": 5, "output_cost": 15},
    "gpt-4o-2024-05-13": {"input_cost": 5, "output_cost": 15},
    "gpt-4-turbo": {"input_cost": 10, "output_cost": 30},
    "gpt-4": {"input_cost": 30, "output_cost": 60},
}


def track_usage(response: ChatCompletion) -> float:
    """
    Args:
        response: The response from the OpenAI API

    OpenAI Model Price

    | Model Name    | Input Cost (per 1M tokens) | Output Cost (per 1M tokens) |
    |---------------|----------------------------|-----------------------------|
    | gpt-3.5-turbo | $0.5                       | $1.5                        |
    | gpt-4o        | $5                         | $15                         |
    | gpt-4-turbo   | $10                        | $30                         |
    | gpt-4         | $30                        | $60                         |

    Returns:
        total_cost (float): The total cost of the response
    """
    llm_model = response.model
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens
    input_cost = (
        OPENAI_MODEL_PRICE[llm_model]["input_cost"]
        * (prompt_tokens + completion_tokens)
        / 1e6
    )
    output_cost = OPENAI_MODEL_PRICE[llm_model]["output_cost"] * completion_tokens / 1e6
    logger.debug(f"Input Cost: ${input_cost}")
    logger.debug(f"Output Cost: ${output_cost}")
    total_cost = input_cost + output_cost
    logger.debug(f"Total Cost: ${total_cost}")
    return total_cost
