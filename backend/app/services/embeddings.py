from openai import AsyncOpenAI

from app.config import settings

_client = None


def get_openai_client():
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


async def embed_texts(texts):
    if not texts:
        return []
    client = get_openai_client()
    response = await client.embeddings.create(
        model=settings.embedding_model,
        input=texts,
    )
    return [item.embedding for item in response.data]
