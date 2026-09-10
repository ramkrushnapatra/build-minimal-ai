from pathlib import Path

from pypdf import PdfReader


def load_document(file_path: str, content_type: str) -> str:
    path = Path(file_path)

    if content_type == "application/pdf":
        reader = PdfReader(path)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)

    return path.read_text(encoding="utf-8", errors="replace")
