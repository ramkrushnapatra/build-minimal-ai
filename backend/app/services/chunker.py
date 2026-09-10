from app.config import settings


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping chunks by character count."""
    text = text.strip()
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    size = settings.chunk_size
    overlap = settings.chunk_overlap

    while start < len(text):
        end = start + size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap

    return chunks
