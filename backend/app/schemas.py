from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: str
    filename: str
    content_type: str
    status: Literal["pending", "processing", "ready", "failed"]
    error_message: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class JobOut(BaseModel):
    id: str
    document_id: str
    status: Literal["queued", "running", "completed", "failed"]
    error_message: str | None
    created_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    document_ids: list[str] | None = None


class Citation(BaseModel):
    document_id: str
    filename: str
    chunk_text: str
    score: float
