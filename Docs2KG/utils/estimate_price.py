def estimate_price(token_count: int, model_name: str = "gpt-3.5-turbo") -> float:
    """
    Estimate the price for the token count
    Args:
        token_count (int): Number of tokens
        model_name (str): Model name to estimate the price
            Choices: "gpt-3.5-turbo", "gpt-4o", "gpt-4-turbo"

    Returns:
        price_in_usd (float): Price in USD


    - Model: gpt-3.5-turbo => Price US$0.50 / 1M tokens (Input), US1.50 / 1M tokens (Output)

    """
    if model_name == "gpt-3.5-turbo":
        return 2 * 2 * token_count / 1000000
    if model_name == "gpt-4o":
        return 2 * 20 * token_count / 1000000
    if model_name == "gpt-4-turbo":
        return 2 * 40 * token_count / 1000000
    raise ValueError(f"Model {model_name} is not supported")
