from __future__ import annotations

import logging

from app.config import settings
from app.schemas import QueryResponse, SourceSnippet
from app.services.embeddings import embed_texts, get_openai_client

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful assistant answering questions using the user's saved notes and URLs.
Use only the provided context. If the context is insufficient, say so clearly.
Reference which sources you used when relevant."""


async def run_query(question: str) -> QueryResponse:
    from app.services.vectorstore import search

    logger.info("Query received: %s", question[:80])

    embeddings = await embed_texts([question])
    hits = await search(embeddings[0], settings.top_k)

    sources = [
        SourceSnippet(
            item_id=h["item_id"],
            title=h["title"],
            snippet=h["chunk_text"][:300],
            score=h["score"],
        )
        for h in hits
    ]

    if not settings.openai_api_key:
        return QueryResponse(
            answer="OpenAI API key not configured. Set OPENAI_API_KEY in backend/.env",
            sources=sources,
        )

    context = "\n\n".join(
        f"[{i}] ({h['title']}): {h['chunk_text']}" for i, h in enumerate(hits, 1)
    )
    user_content = (
        f"Context:\n{context}\n\nQuestion: {question}" if context
        else f"No relevant context found.\n\nQuestion: {question}"
    )

    client = get_openai_client()
    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )

    answer = response.choices[0].message.content or ""
    logger.info("Query answered with %d sources", len(sources))
    return QueryResponse(answer=answer, sources=sources)
