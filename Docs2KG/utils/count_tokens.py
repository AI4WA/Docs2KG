import tiktoken


def count_tokens(text, model_name="cl100k_base") -> int:
    """
    Count the number of tokens in the text
    Args:
        text:
        model_name:

    Returns:
        total_token (int): The number of tokens in the text

    """
    enc = tiktoken.get_encoding(model_name)
    tokens = enc.encode(text)
    return len(tokens)
