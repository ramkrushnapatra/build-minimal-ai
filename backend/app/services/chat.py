from __future__ import annotations

from app.config import settings
from app.schemas import Citation
from app.services.embeddings import get_openai_client
from app.services.vectorstore import search


SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on the provided context.
Use only the context below to answer. If the context doesn't contain enough information, say so clearly.
Cite which source documents you used when relevant."""


async def retrieve_context(message: str, document_ids: list[str] | None) -> tuple[str, list[Citation]]:
    from app.services.embeddings import embed_texts

    embeddings = await embed_texts([message])
    hits = await search(embeddings[0], settings.top_k, document_ids)

    if not hits:
        return "", []

    context_parts = []
    citations: list[Citation] = []
    for i, hit in enumerate(hits, 1):
        context_parts.append(f"[{i}] ({hit['filename']}): {hit['chunk_text']}")
        citations.append(Citation(
            document_id=hit["document_id"],
            filename=hit["filename"],
            chunk_text=hit["chunk_text"][:300],
            score=hit["score"],
        ))

    return "\n\n".join(context_parts), citations


async def stream_chat(message: str, document_ids: list[str] | None):
    context, citations = await retrieve_context(message, document_ids)

    yield {"type": "citations", "data": [c.model_dump() for c in citations]}

    if not settings.openai_api_key:
        yield {"type": "token", "data": "OpenAI API key not configured. Set OPENAI_API_KEY in .env"}
        yield {"type": "done", "data": None}
        return

    client = get_openai_client()
    user_content = f"Context:\n{context}\n\nQuestion: {message}" if context else message

    stream = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        stream=True,
    )

    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield {"type": "token", "data": delta}

    yield {"type": "done", "data": None}
