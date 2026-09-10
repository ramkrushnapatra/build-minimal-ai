from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: str
    filename: str
    content_type: str
    status: Literal["pending", "processing", "ready", "failed"]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class JobOut(BaseModel):
    id: str
    document_id: str
    status: Literal["queued", "running", "completed", "failed"]
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    document_ids: Optional[List[str]] = None


class Citation(BaseModel):
    document_id: str
    filename: str
    chunk_text: str
    score: float
