from datetime import datetime
from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, Field, HttpUrl


class NoteIngest(BaseModel):
    type: Literal["note"]
    content: str = Field(..., min_length=1, max_length=50000)


class UrlIngest(BaseModel):
    type: Literal["url"]
    url: HttpUrl


IngestRequest = Annotated[Union[NoteIngest, UrlIngest], Field(discriminator="type")]


class ItemOut(BaseModel):
    id: str
    source_type: Literal["note", "url"]
    title: str
    url: Optional[str]
    status: Literal["processing", "indexed", "failed"]
    error_message: Optional[str]
    created_at: datetime
    preview: str

    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class SourceSnippet(BaseModel):
    item_id: str
    title: str
    snippet: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceSnippet]
