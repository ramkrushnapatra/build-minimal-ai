import logging

from app.database import async_session
from app.models import Item, ItemStatus
from app.services.chunker import chunk_text
from app.services.embeddings import embed_texts
from app.services.vectorstore import upsert_chunks

logger = logging.getLogger(__name__)


async def index_item(item_id):
    async with async_session() as session:
        item = await session.get(Item, item_id)
        if not item:
            logger.error("Item %s not found", item_id)
            return

        try:
            chunks = chunk_text(item.raw_content)
            if not chunks:
                raise ValueError("No content to index")

            embeddings = await embed_texts(chunks)
            await upsert_chunks(item.id, item.title, chunks, embeddings)

            item.status = ItemStatus.INDEXED
            item.error_message = None
            logger.info("Item %s indexed", item_id)
        except Exception as exc:
            item.status = ItemStatus.FAILED
            item.error_message = str(exc)
            logger.exception("Failed to index item %s", item_id)

        await session.commit()
