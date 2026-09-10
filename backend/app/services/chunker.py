from app.core.config import settings


def chunk_text(text):
    text = text.strip()
    if not text:
        return []

    chunks = []
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
