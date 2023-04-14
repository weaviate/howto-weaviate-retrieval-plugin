import openai


def get_embedding(text):
    """
    Get the embedding for a given text
    """
    results = openai.Embedding.create(input=text, model="text-embedding-ada-002")

    return results["data"][0]["embedding"]
