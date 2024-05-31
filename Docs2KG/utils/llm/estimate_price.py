def estimate_price(token_count: int, model_name: str = "gpt-3.5-turbo") -> float:
    """
    Estimate the price for the token count, for different models.

    Current, we will use the gpt to extract layout and content structure from the document.

    So roughly input and output tokens are the same
    So we will have (input price + output price) * token_count * call_it_twice

    Args:
        token_count (int): Number of tokens
        model_name (str): Model name to estimate the price
            Choices: "gpt-3.5-turbo", "gpt-4o", "gpt-4-turbo"

    Returns:
        price_in_usd (float): Price in USD


    - Model: gpt-3.5-turbo => Price US$0.50 / 1M tokens (Input), US1.50 / 1M tokens (Output)

    """
    if model_name == "gpt-3.5-turbo":
        return 2 * token_count * 2 / 1000000
    if model_name == "gpt-4o":
        return 2 * token_count * 20 / 1000000
    if model_name == "gpt-4-turbo":
        return 2 * token_count * 40 / 1000000
    raise ValueError(f"Model {model_name} is not supported")
