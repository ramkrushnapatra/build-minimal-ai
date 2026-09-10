# build-minimal-ai

A minimal document Q&A application powered by Retrieval-Augmented Generation (RAG). Upload PDFs or text files, then ask questions and get answers grounded in your documents with source citations.

**Live repo:** https://github.com/ramkrushnapatra/build-minimal-ai

## Architecture

```
┌─────────────┐     REST + SSE      ┌──────────────┐
│  Next.js    │ ◄─────────────────► │   FastAPI    │
│  Frontend   │                     │   Backend    │
└─────────────┘                     └──────┬───────┘
                                             │
                              ┌──────────────┼──────────────┐
                              ▼              ▼              ▼
                         SQLite DB     ChromaDB       OpenAI API
                        (metadata)    (vectors)    (embed + chat)
```

## Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | Next.js 15, TypeScript, Tailwind | Modern React with App Router, type safety |
| Backend | FastAPI, Python 3.12 | Async-native, great for streaming SSE |
| Vector DB | ChromaDB | Zero-config local persistence, no extra infra |
| Embeddings | OpenAI text-embedding-3-small | High quality, simple API |
| LLM | OpenAI gpt-4o-mini | Cost-effective, fast streaming |
| Job queue | FastAPI BackgroundTasks | Lightweight async ingestion without Redis |

## Features

- **Document upload** — PDF, TXT, Markdown via drag-and-drop
- **Async ingestion** — Background chunking, embedding, and vector indexing with job status polling
- **RAG chat** — Semantic search over uploaded docs with SSE-streamed answers
- **Citations** — Source references with relevance scores shown below each answer
- **Document filtering** — Select specific documents to scope your queries

## Local Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- OpenAI API key

### 1. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY

uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

### Docker (optional)

```bash
cp backend/.env.example backend/.env
# Set OPENAI_API_KEY in backend/.env

docker compose up --build
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/documents/upload` | Upload a document |
| POST | `/api/documents/{id}/ingest` | Start async ingestion |
| GET | `/api/documents` | List all documents |
| GET | `/api/jobs/{id}` | Poll ingestion job status |
| POST | `/api/chat` | Stream chat response (SSE) |
| GET | `/health` | Health check |

## Design Decisions & Tradeoffs

### Why separate frontend and backend?

Python dominates the AI/ML ecosystem (ChromaDB, OpenAI SDK, PDF parsing). FastAPI's async model pairs naturally with SSE streaming. A decoupled architecture lets each layer deploy independently.

### Why ChromaDB over pgvector/Pinecone?

ChromaDB runs locally with zero setup — ideal for a minimal MVP and local evaluation. Tradeoff: not suited for multi-tenant production at scale. For production, I'd migrate to pgvector (reuse Postgres) or a managed service like Pinecone.

### Why FastAPI BackgroundTasks instead of Celery/Redis?

The assignment calls for async workflows, but adding Redis + workers adds operational complexity disproportionate to the scope. BackgroundTasks handles ingestion jobs cleanly for a single-instance deployment. At scale, I'd introduce a proper task queue (Celery, ARQ, or Taskiq).

### Chunking strategy

Fixed-size character chunks (800 chars, 150 overlap). Simple and predictable. Tradeoff: may split mid-sentence. A production system would use semantic or recursive splitting (e.g., LangChain's RecursiveCharacterTextSplitter with sentence boundaries).

### SSE over WebSockets

SSE is simpler for unidirectional LLM token streaming, works over HTTP/2, and needs no connection management on the client. WebSockets would be better for bidirectional real-time features (typing indicators, multi-user).

### No authentication

Keeps the MVP focused on core RAG flow. Production would add JWT auth, per-user document isolation, and rate limiting.

## Project Structure

```
build-minimal-ai/
├── backend/
│   ├── app/
│   │   ├── api/          # Route handlers
│   │   ├── services/     # RAG pipeline, embeddings, chat
│   │   ├── models.py     # SQLAlchemy models
│   │   ├── schemas.py    # Pydantic schemas
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/          # Next.js pages
│       ├── components/   # Upload, chat, document list
│       └── lib/          # API client
├── data/                 # Runtime data (gitignored)
└── docker-compose.yml
```
