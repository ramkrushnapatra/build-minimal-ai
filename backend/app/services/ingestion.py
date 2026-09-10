from datetime import datetime, timezone

from sqlalchemy import select

from app.database import async_session
from app.models import Document, DocumentStatus, Job, JobStatus
from app.services.chunker import chunk_text
from app.services.embeddings import embed_texts
from app.services.loader import load_document
from app.services.vectorstore import upsert_chunks


async def run_ingestion_job(job_id: str):
    async with async_session() as session:
        job = await session.get(Job, job_id)
        if not job:
            return

        job.status = JobStatus.RUNNING
        await session.commit()

        doc = await session.get(Document, job.document_id)
        if not doc:
            job.status = JobStatus.FAILED
            job.error_message = "Document not found"
            await session.commit()
            return

        try:
            text = load_document(doc.file_path, doc.content_type)
            chunks = chunk_text(text)
            if not chunks:
                raise ValueError("No text content extracted from document")

            embeddings = await embed_texts(chunks)
            await upsert_chunks(doc.id, doc.filename, chunks, embeddings)

            doc.status = DocumentStatus.READY
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)
        except Exception as exc:
            doc.status = DocumentStatus.FAILED
            doc.error_message = str(exc)
            job.status = JobStatus.FAILED
            job.error_message = str(exc)
            job.completed_at = datetime.now(timezone.utc)

        await session.commit()
