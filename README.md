# AI Knowledge Inbox

A minimal production-style web app built for the **Turium AI Interview Assignment**.

Users can save short notes or URLs, then ask questions over their saved content and get answers powered by a simple RAG pipeline.

**Repo:** https://github.com/ramkrushnapatra/build-minimal-ai

---

## Features (per assignment)

### 1. Content Ingestion
- Add plain-text notes
- Add URLs (page content fetched server-side)
- Stores raw content + metadata (timestamp, source type)
- No auth — single-user

### 2. Semantic Search + RAG
- Chunking with overlap
- Embeddings via OpenAI
- Vector storage in ChromaDB
- Question → top relevant chunks → LLM → answer with cited sources

### 3. Frontend (React)
- Note / URL input form
- List of saved items
- Ask-question interface
- Answer + source snippets display
- React hooks for state management

### 4. API
| Method | Path | Body | Response |
|--------|------|------|----------|
| POST | `/ingest` | `{type:"note", content:"..."}` or `{type:"url", url:"..."}` | Saved item |
| GET | `/items` | — | List of all items |
| POST | `/query` | `{question:"..."}` | `{answer, sources[]}` |

---

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React (Vite), hooks, Tailwind |
| Backend | FastAPI, Python |
| Metadata DB | SQLite |
| Vector store | ChromaDB |
| LLM + Embeddings | OpenAI API |

---

## Prerequisites

- Python 3.9+
- Node.js 18+
- OpenAI API key — get one at https://platform.openai.com/api-keys (new accounts usually get free starter credit)

---

## Local Setup

### 1. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Create `backend/.env` from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your key:

```
OPENAI_API_KEY=sk-your-key-here
```

Start the server:

```bash
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**

### 3. Docker (optional)

```bash
cp backend/.env.example backend/.env
# add OPENAI_API_KEY in backend/.env

docker compose up --build
```

Frontend: http://localhost:3000 | Backend: http://localhost:8000

---

## Design Decisions & Tradeoffs

### Chunking
800-character windows with 150-character overlap. Simple and intentional for an MVP. May split mid-sentence. At scale, switch to recursive or semantic chunking.

### Vector store — ChromaDB
Zero-config local persistence, no extra infrastructure. Good for single-user local use. At scale with many users, migrate to pgvector or a managed service like Pinecone.

### Async indexing
FastAPI `BackgroundTasks` handles chunking + embedding after ingest. Enough for this assignment. At scale, use Celery/Redis for a proper job queue.

### URL fetching
Server-side fetch with httpx + BeautifulSoup. Works for static pages. SPAs and JS-heavy sites may return thin content. Production would use a headless browser or readability API.

### What breaks at scale
- Single-process background tasks block under heavy load
- ChromaDB on local disk is not multi-tenant
- No rate limiting or auth
- SQLite is fine for one user, not for concurrent multi-user writes

### Production changes
- Add authentication and per-user data isolation
- Move to a task queue (Celery, ARQ) for ingestion
- Use managed vector DB + Postgres
- Add rate limiting, monitoring, and structured log aggregation
- Cache frequent queries

### Debuggability
- Structured logging on all API routes and services
- Clear HTTP error messages (400 for bad input, 422 for URL fetch fail, 500 for server errors)
- Item status field (`processing` / `indexed` / `failed`) with error messages visible in the UI

---

## Project Structure

```
build-minimal-ai/
├── backend/
│   └── app/
│       ├── api/           ingest.py, items.py, query.py
│       ├── services/      chunker, embeddings, vectorstore, indexer, url_fetcher, query
│       ├── models.py      Item model (note | url)
│       ├── database.py    SQLite setup
│       └── main.py
├── frontend/
│   └── src/
│       ├── components/    InboxForm, ItemList, QueryPanel
│       ├── App.jsx        main layout
│       └── api.js         API calls
├── data/                  runtime DB + vectors (gitignored)
└── docker-compose.yml
```
