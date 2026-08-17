from google import genai

from app.core.config import settings


client = genai.Client(
    api_key=settings.gemini_api_key
)


def stream_generate(prompt: str):

    response = client.models.generate_content_stream(
        model=settings.gemini_model,
        contents=prompt,
    )

    for chunk in response:

        if chunk.text:
            yield chunk.text