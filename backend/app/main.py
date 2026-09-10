from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ingest, items, query
from app.config import settings
from app.database import init_db
from app.logging_config import setup_logging


@asynccontextmanager
async def lifespan(app):
    setup_logging()
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    await init_db()
    yield


app = FastAPI(title="AI Knowledge Inbox", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router)
app.include_router(items.router)
app.include_router(query.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
