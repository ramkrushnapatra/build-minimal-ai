# AI Knowledge Inbox

A minimal production-style web app for the **Turium AI Interview Assignment**.

Save short notes or URLs, then ask questions over your saved content — powered by a simple RAG pipeline.

## What it does

1. **Save content** — plain-text notes or URLs (fetched server-side)
2. **Index async** — chunk → embed → store in ChromaDB
3. **Ask questions** — semantic search + LLM answer with cited sources

## Stack

| Layer | Tech |
|-------|------|
| Frontend | **React** (Vite), hooks, Tailwind |
| Backend | FastAPI, Python |
| Vector store | ChromaDB |
| DB | SQLite (item metadata) |
| LLM | OpenAI API |

## API (as per assignment)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/ingest` | Save a note `{type:"note", content:"..."}` or URL `{type:"url", url:"..."}` |
| GET | `/items` | List all saved items |
| POST | `/query` | Ask `{question:"..."}` → `{answer, sources[]}` |

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env          # set OPENAI_API_KEY
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Design tradeoffs

**Chunking:** 800-char windows with 150-char overlap. Simple and fast; may split mid-sentence. At scale, use semantic/recursive splitting.

**Vector store:** ChromaDB — zero-config local persistence. Fine for single-user MVP; migrate to pgvector/Pinecone for multi-tenant production.

**Async indexing:** FastAPI `BackgroundTasks` indexes content after ingest. Sufficient for this scope; use Celery/Redis at higher throughput.

**URL fetching:** Server-side httpx + BeautifulSoup. No JS rendering — SPAs may return thin content. Production would add a headless browser or readability API.

**No auth:** Single-user by design per assignment spec.

## Project structure

```
backend/app/
  api/          ingest.py, items.py, query.py
  services/     chunker, embeddings, vectorstore, indexer, url_fetcher, query
  models.py     Item (note | url)
frontend/src/
  components/   InboxForm, ItemList, QueryPanel
  App.tsx       main layout with hooks
```
