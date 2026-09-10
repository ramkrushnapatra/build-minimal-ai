import logging
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Item, ItemStatus, SourceType
from app.schemas import IngestRequest, ItemOut, NoteIngest, UrlIngest
from app.services.indexer import index_item
from app.services.url_fetcher import fetch_url_content

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ingest"])


def to_item_out(item: Item) -> ItemOut:
    preview = item.raw_content[:200] + ("..." if len(item.raw_content) > 200 else "")
    return ItemOut(
        id=item.id,
        source_type=item.source_type.value,
        title=item.title,
        url=item.url,
        status=item.status.value,
        error_message=item.error_message,
        created_at=item.created_at,
        preview=preview,
    )


@router.post("/ingest", response_model=ItemOut, status_code=201)
async def ingest(
    body: IngestRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    item_id = str(uuid.uuid4())

    if isinstance(body, NoteIngest):
        content = body.content.strip()
        title = content.split("\n")[0][:200] or "Untitled note"
        item = Item(
            id=item_id,
            source_type=SourceType.NOTE,
            title=title,
            raw_content=content,
            status=ItemStatus.PROCESSING,
        )
        logger.info("Ingesting note %s (%d chars)", item_id, len(content))

    elif isinstance(body, UrlIngest):
        url = str(body.url)
        try:
            title, content = await fetch_url_content(url)
        except Exception as exc:
            logger.warning("URL fetch failed for %s: %s", url, exc)
            raise HTTPException(status_code=422, detail=f"Could not fetch URL: {exc}")

        item = Item(
            id=item_id,
            source_type=SourceType.URL,
            title=title,
            raw_content=content,
            url=url,
            status=ItemStatus.PROCESSING,
        )
        logger.info("Ingesting URL %s as item %s", url, item_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid ingest type")

    session.add(item)
    await session.commit()
    await session.refresh(item)

    background_tasks.add_task(index_item, item.id)
    return to_item_out(item)
