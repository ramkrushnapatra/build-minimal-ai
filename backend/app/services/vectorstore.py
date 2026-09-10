import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings

COLLECTION_NAME = "documents"

_client: chromadb.PersistentClient | None = None


def get_chroma_client() -> chromadb.PersistentClient:
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


async def upsert_chunks(
    document_id: str,
    filename: str,
    chunks: list[str],
    embeddings: list[list[float]],
):
    collection = get_collection()
    ids = [f"{document_id}_{i}" for i in range(len(chunks))]
    metadatas = [
        {"document_id": document_id, "filename": filename, "chunk_index": i}
        for i in range(len(chunks))
    ]
    collection.upsert(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)


async def search(query_embedding: list[float], top_k: int, document_ids: list[str] | None = None):
    collection = get_collection()
    where = None
    if document_ids:
        where = {"document_id": {"$in": document_ids}}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where,
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
            "document_id": meta["document_id"],
            "filename": meta["filename"],
            "chunk_text": doc,
            "score": 1 - dist,
        })
    return hits


def delete_document_vectors(document_id: str):
    collection = get_collection()
    existing = collection.get(where={"document_id": document_id})
    if existing["ids"]:
        collection.delete(ids=existing["ids"])
