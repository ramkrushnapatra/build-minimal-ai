import logging

from fastapi import APIRouter, HTTPException, Request

from app.services.query import run_query

logger = logging.getLogger(__name__)
router = APIRouter(tags=["query"])


@router.post("/query")
async def query(request: Request):
    data = await request.json()
    question = data.get("question", "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    try:
        return await run_query(question)
    except Exception as exc:
        logger.exception("Query failed")
        raise HTTPException(status_code=500, detail=f"Query failed: {exc}")
