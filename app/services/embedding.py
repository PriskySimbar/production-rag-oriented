from google import genai

from app.core.config import settings


client = genai.Client(
    api_key=settings.gemini_api_key
)


def generate_embeddings(
    texts: list[str],
) -> list[list[float]]:

    if not texts:
        return []

    response = client.models.embed_content(
    model="gemini-embedding-001",
    contents=texts,
    config={
        "output_dimensionality": 768
    },
)

    return [
        embedding.values
        for embedding in response.embeddings
    ]