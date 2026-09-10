import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.ingest import format_item
from app.database import get_session
from app.database.models import Item

logger = logging.getLogger(__name__)
router = APIRouter(tags=["items"])


@router.get("/items")
async def list_items(session=Depends(get_session)):
    result = await session.execute(select(Item).order_by(Item.created_at.desc()))
    items = result.scalars().all()
    logger.info("Listed %d items", len(items))
    return [format_item(item) for item in items]
