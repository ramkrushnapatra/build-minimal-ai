import logging

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "knowledge_inbox"
_client = None


def get_chroma_client():
    global _client
    if _client is None:
        settings.chroma_dir.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(
            path=str(settings.chroma_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _client


def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


async def upsert_chunks(item_id, title, chunks, embeddings):
    collection = get_collection()
    ids = [f"{item_id}_{i}" for i in range(len(chunks))]
    metadatas = [
        {"item_id": item_id, "title": title, "chunk_index": i}
        for i in range(len(chunks))
    ]
    collection.upsert(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)
    logger.info("Indexed %d chunks for item %s", len(chunks), item_id)


async def search(query_embedding, top_k):
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    hits = []
    if not results["documents"] or not results["documents"][0]:
        return hits

    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hits.append({
            "item_id": meta["item_id"],
            "title": meta["title"],
            "chunk_text": doc,
            "score": round(1 - dist, 4),
        })
    return hits
