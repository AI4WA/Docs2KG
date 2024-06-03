from openai import OpenAI

client = OpenAI()


def get_openai_embedding(text: str, llm_emb_model: str = "text-embedding-3-small"):
    """
    Get the embedding from OpenAI API

    Args:
        text (str): The text to get the embedding
        llm_emb_model (str): The name of the LLM model

    Returns:
        str: The embedding of the text
    """
    response = client.embeddings.create(input=text, model=llm_emb_model)

    return response.data[0].embedding
