import json

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.schemas import ChatRequest
from app.services.chat import stream_chat

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
async def chat(request: ChatRequest):
    async def event_generator():
        async for event in stream_chat(request.message, request.document_ids):
            yield {"event": event["type"], "data": json.dumps(event["data"])}

    return EventSourceResponse(event_generator())
