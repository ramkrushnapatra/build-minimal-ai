import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.ingest import to_item_out
from app.database import get_session
from app.models import Item
from app.schemas import ItemOut

logger = logging.getLogger(__name__)
router = APIRouter(tags=["items"])


@router.get("/items", response_model=list[ItemOut])
async def list_items(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Item).order_by(Item.created_at.desc()))
    items = result.scalars().all()
    logger.info("Listed %d items", len(items))
    return [to_item_out(item) for item in items]
