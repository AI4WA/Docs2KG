import tiktoken


def count_tokens(text, model_name="cl100k_base") -> int:
    """
    Count the number of tokens in the text

    References: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb

    | Encoding name | OpenAI models                                                                                 |
    |---------------|-----------------------------------------------------------------------------------------------|
    | cl100k_base   | gpt-4, gpt-3.5-turbo, text-embedding-ada-002, text-embedding-3-small, text-embedding-3-large  |
    | p50k_base     | Codex models, text-davinci-002, text-davinci-003                                              |
    | r50k_base (or gpt2) | GPT-3 models like davinci                                                               |

    Args:
        text (str): The text to count the tokens
        model_name (str): The model name to use for tokenization. Default is "cl100k_base"


    Returns:
        total_token (int): The number of tokens in the text

    """
    enc = tiktoken.get_encoding(model_name)
    tokens = enc.encode(text)
    return len(tokens)
