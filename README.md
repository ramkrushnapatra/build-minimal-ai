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

## Local Setup (Windows)

### 1. Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend\.env` from the example:

```powershell
copy .env.example .env
```

Edit `.env` and add your key:

```
OPENAI_API_KEY=sk-your-key-here
```

Start the server:

```powershell
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

Open a new terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000**

### 3. Docker (optional)

```powershell
copy backend\.env.example backend\.env
```

Add `OPENAI_API_KEY` in `backend\.env`, then run:

```powershell
docker compose up --build
```

Frontend: http://localhost:3000 | Backend: http://localhost:8000

---

## Design Decisions & Tradeoffs

### 1. Chunking approach

**What I chose:** Fixed-size character chunking — 800 characters per chunk, 150 characters overlap between chunks.

**How it works:** The text is cut into equal-sized blocks by character count. Each new chunk starts 150 characters before the previous chunk ended, so context is not lost at boundaries.

**Example of "may split mid-sentence":**
```
Original text:
"FastAPI is a modern Python framework. It supports async requests and is easy to use."

Chunk 1 (chars 0–800):   "...Python framework. It supports async requ"
Chunk 2 (chars 650–1450): "...async requests and is easy to use."
```
The first chunk can end halfway through a word or sentence because the cut is by character count, not by paragraph or sentence.

**Why this approach:**
- Simple to implement and easy to reason about
- Predictable chunk sizes for embedding API calls
- Overlap (150 chars) reduces the chance that an answer spans a hard cut and gets missed in search
- Good enough for short notes and small articles in an MVP

**Tradeoff:** Search quality can drop when meaning is split across chunks. A question about one sentence may only partially match two chunks.

**At scale:** Switch to recursive chunking (split by paragraph → sentence → word) or semantic chunking (split when embedding similarity drops).

---

### 2. Vector store choice

**What I chose:** ChromaDB (local persistent storage in `data/chroma/`)

**Why:**
- No separate server to install or manage
- Works out of the box on Windows for local development
- Stores vectors on disk, so data survives restarts
- Fits the assignment requirement for a lightweight vector store

**Tradeoff:** Not built for many users or millions of documents on one machine.

**At scale:** Move to pgvector (if you already use Postgres) or a managed service like Pinecone/Qdrant.

---

### 3. What breaks at scale

| Area | Current limit |
|------|---------------|
| Background indexing | `BackgroundTasks` runs in the same process — heavy uploads can slow API responses |
| ChromaDB | Single local instance, not designed for multi-tenant isolation |
| SQLite | Fine for one user; concurrent writes from many users will cause lock issues |
| OpenAI API | No rate limiting or retry backoff — bursts can fail or get expensive |
| URL fetching | No caching — fetching the same URL twice re-downloads everything |

---

### 4. Production changes

- **Auth:** Add user accounts so each person only sees their own notes/URLs
- **Job queue:** Replace `BackgroundTasks` with Celery/Redis for reliable async ingestion
- **Database:** Postgres for metadata, pgvector or Pinecone for vectors
- **Chunking:** Recursive or semantic splitting for better retrieval quality
- **Observability:** Metrics, alerting, and centralized logs (e.g. Datadog, Sentry)
- **Rate limiting:** Protect `/query` and `/ingest` from abuse and control OpenAI costs
- **URL cache:** Store fetched page content with TTL to avoid re-fetching

---

### Other decisions

**Async indexing:** FastAPI `BackgroundTasks` runs chunking + embedding after ingest returns. Keeps the API simple for this assignment.

**URL fetching:** httpx + BeautifulSoup strips HTML to plain text. Works for static pages; JavaScript-rendered sites may return little or no content.

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
│       ├── api/              ingest.py, items.py, query.py
│       ├── core/             config.py, logging.py
│       ├── database/         connection.py, models.py
│       ├── services/         chunker, embeddings, vectorstore, indexer, url_fetcher, query
│       └── main.py
├── frontend/
│   └── src/
│       ├── components/    InboxForm, ItemList, QueryPanel
│       ├── App.jsx        main layout
│       └── api.js         API calls
├── data/                  runtime DB + vectors (gitignored)
└── docker-compose.yml
```
