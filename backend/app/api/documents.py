import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_session
from app.models import Document, DocumentStatus, Job, JobStatus
from app.schemas import DocumentOut, JobOut
from app.services.ingestion import run_ingestion_job

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_TYPES = {
    "application/pdf": ".pdf",
    "text/plain": ".txt",
    "text/markdown": ".md",
}


@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
):
    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Unsupported file type: {content_type}")

    doc_id = str(uuid.uuid4())
    ext = ALLOWED_TYPES[content_type]
    dest = settings.upload_dir / f"{doc_id}{ext}"
    dest.parent.mkdir(parents=True, exist_ok=True)

    content = await file.read()
    dest.write_bytes(content)

    doc = Document(
        id=doc_id,
        filename=file.filename or f"document{ext}",
        content_type=content_type,
        file_path=str(dest),
        status=DocumentStatus.PENDING,
    )
    session.add(doc)
    await session.commit()
    await session.refresh(doc)
    return doc


@router.get("", response_model=list[DocumentOut])
async def list_documents(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Document).order_by(Document.created_at.desc()))
    return result.scalars().all()


@router.get("/{document_id}", response_model=DocumentOut)
async def get_document(document_id: str, session: AsyncSession = Depends(get_session)):
    doc = await session.get(Document, document_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc


@router.post("/{document_id}/ingest", response_model=JobOut)
async def ingest_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    doc = await session.get(Document, document_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    if doc.status == DocumentStatus.PROCESSING:
        raise HTTPException(409, "Document is already being processed")

    job = Job(document_id=document_id, status=JobStatus.QUEUED)
    doc.status = DocumentStatus.PROCESSING
    session.add(job)
    await session.commit()
    await session.refresh(job)

    background_tasks.add_task(run_ingestion_job, job.id)
    return job


@router.delete("/{document_id}")
async def delete_document(document_id: str, session: AsyncSession = Depends(get_session)):
    doc = await session.get(Document, document_id)
    if not doc:
        raise HTTPException(404, "Document not found")

    file_path = Path(doc.file_path)
    if file_path.exists():
        file_path.unlink()

    await session.delete(doc)
    await session.commit()
    return {"deleted": True}
