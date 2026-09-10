import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, String, Text, func

from app.database.connection import Base


class SourceType(str, enum.Enum):
    NOTE = "note"
    URL = "url"


class ItemStatus(str, enum.Enum):
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class Item(Base):
    __tablename__ = "items"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_type = Column(Enum(SourceType))
    title = Column(String(500))
    raw_content = Column(Text)
    url = Column(String(2000), nullable=True)
    status = Column(Enum(ItemStatus), default=ItemStatus.PROCESSING)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
