import logging
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request

from app.database import get_session
from app.models import Item, ItemStatus, SourceType
from app.services.indexer import index_item
from app.services.url_fetcher import fetch_url_content

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ingest"])


def format_item(item):
    preview = item.raw_content[:200]
    if len(item.raw_content) > 200:
        preview += "..."
    return {
        "id": item.id,
        "source_type": item.source_type.value,
        "title": item.title,
        "url": item.url,
        "status": item.status.value,
        "error_message": item.error_message,
        "created_at": item.created_at,
        "preview": preview,
    }


@router.post("/ingest", status_code=201)
async def ingest(request: Request, background_tasks: BackgroundTasks, session=Depends(get_session)):
    data = await request.json()
    item_type = data.get("type", "")
    item_id = str(uuid.uuid4())

    if item_type == "note":
        content = data.get("content", "").strip()
        if not content:
            raise HTTPException(status_code=400, detail="Note content is required")

        title = content.split("\n")[0][:200] or "Untitled note"
        item = Item(
            id=item_id,
            source_type=SourceType.NOTE,
            title=title,
            raw_content=content,
            status=ItemStatus.PROCESSING,
        )
        logger.info("Ingesting note %s", item_id)

    elif item_type == "url":
        url = data.get("url", "").strip()
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")

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
        logger.info("Ingesting URL %s", url)
    else:
        raise HTTPException(status_code=400, detail="Type must be note or url")

    session.add(item)
    await session.commit()
    await session.refresh(item)

    background_tasks.add_task(index_item, item.id)
    return format_item(item)
