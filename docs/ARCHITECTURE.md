# AI Business OS — Architecture Deep Dive

## 1. System Overview

AI Business OS is a multi-tenant AI platform composed of four planes:

1. **Client plane** — Flutter mobile app (and any HTTP client) talking JSON/SSE over HTTPS.
2. **API plane** — Nginx reverse proxy → async FastAPI. Stateless; horizontally scalable.
3. **Data plane** — PostgreSQL (system of record), Redis (cache/broker/pubsub), object storage (uploads), FAISS/Milvus (vectors).
4. **AI plane** — LangGraph agent graphs orchestrating LangChain components: LLM provider abstraction, embeddings, retrievers, OCR, Whisper.

```
┌──────────────┐     ┌───────┐     ┌────────────────────────────┐
│ Flutter App  │────▶│ Nginx │────▶│ FastAPI (uvicorn, async)   │
│ voice/files  │◀────│  TLS  │◀────│  auth · routers · SSE      │
└──────────────┘     └───────┘     └──────┬──────────┬──────────┘
                                          │          │ enqueue
                              sync path   │          ▼
                                          │   ┌──────────────┐   ┌────────┐
                                          │   │ Celery Worker│◀──│ Redis  │
                                          │   │ OCR·Whisper· │   │ broker │
                                          │   │ ingest·report│   └────────┘
                                          ▼   └──────┬───────┘
                                   ┌──────────────┐  │
                                   │  AI Layer    │◀─┘
                                   │ LangGraph →  │
                                   │ LangChain →  │──▶ FAISS / Milvus
                                   │ LLM provider │──▶ OpenAI | local LLM
                                   └──────┬───────┘
                                          ▼
                          PostgreSQL (users, workspaces, docs,
                          conversations, invoices, reports, jobs)
```

### Design principles
- **Sync vs async split.** Anything < ~5s (chat turn, retrieval) is served inline with SSE streaming. Anything heavy (transcription, OCR batch, ingestion, report generation) becomes a Celery job; the client polls `/jobs/{id}` or receives a push notification.
- **Provider abstraction.** `services/llm.py` exposes `get_chat_model()` / `get_embeddings()`. Swapping OpenAI ↔ local (Ollama/vLLM-compatible) is a `.env` change; no module code changes.
- **Workspace isolation.** Every row and every vector is tagged `workspace_id`. Retrieval filters by workspace, so teams never leak data to each other.
- **Everything is a module.** Each capability = one router + one service + (optionally) one agent graph + one Celery task. Adding a module never touches the core.

## 2. Request lifecycles

### 2.1 AI Chat (sync, streaming)
```
POST /api/v1/chat/{conversation_id}/messages
 → auth (JWT) → load conversation history (Postgres)
 → build prompt (system + history window + user msg)
 → llm.stream() → SSE tokens to client
 → persist assistant message → update conversation title if first turn
```

### 2.2 Document Chat (async ingest, sync query)
```
Ingest: POST /documents (multipart)
 → store file → create Document(status=PENDING) → celery: ingest_document
 worker: load (pypdf/docx/pptx) → chunk (Recursive, 1000/150 overlap)
        → embed (sentence-transformers) → upsert FAISS(workspace index)
        → Document(status=READY, chunk_count=n)

Query: POST /documents/{id}/chat
 → embed question → FAISS similarity (k=6, filter doc_id+workspace)
 → stuff context → LLM answer with citations [chunk#]
```

### 2.3 Meeting Summarizer (fully async)
```
POST /meetings (audio upload) → celery: transcribe_meeting
 worker: Whisper(audio) → transcript
        → map-reduce summary chain → {summary, decisions, action_items[]}
        → persist → push notification to uploader
```

### 2.4 Invoice Reader (OCR pipeline)
```
POST /invoices → celery: process_invoice
 worker: pdf→images (pypdfium2) → Tesseract OCR → raw text
        → LLM structured extraction (Pydantic schema: vendor, date,
          line_items[], subtotal, tax, total, currency)
        → validation (totals reconcile) → persist Invoice
```

## 3. Agent architecture (LangGraph)

### 3.1 Research Agent — plan → act → synthesize
```
        ┌─────────┐
  in ──▶│ planner │ produces sub-questions
        └────┬────┘
             ▼
        ┌─────────┐   loops until all sub-questions answered
        │ searcher│◀─────────────┐ (web/KB tools)
        └────┬────┘              │
             ▼                   │
        ┌─────────┐  needs more? │
        │ critic  │──────────────┘
        └────┬────┘
             ▼
        ┌────────────┐
        │ synthesizer│──▶ cited report
        └────────────┘
```
State: `ResearchState {question, plan[], findings[], iterations, report}` with a hard iteration cap.

### 3.2 Multi-Agent Workflow — supervisor pattern
```
                 ┌────────────┐
        task ───▶│ SUPERVISOR │ routes with structured output
                 └─┬───┬───┬──┘
          ┌────────┘   │   └─────────┐
          ▼            ▼             ▼
     ┌─────────┐ ┌──────────┐ ┌───────────┐
     │Researcher│ │ Writer   │ │ Analyst   │  each returns to supervisor
     └─────────┘ └──────────┘ └───────────┘
                 supervisor → FINISH → final answer
```
The supervisor is an LLM node with an enum-constrained decision (`next: researcher|writer|analyst|FINISH`). Worker results append to shared message state. Guard: max 12 hops.

### 3.3 Email & Coding assistants
Single-node graphs today (prompted LLM with tools), kept as graphs so tools
(calendar lookup, repo context) can be attached without API changes.

## 4. RAG subsystem
```
services/rag/
├── loaders.py     pdf/docx/pptx/html/youtube-transcript → text
├── chunker.py     recursive splitter, tiktoken-aware
├── embeddings.py  sentence-transformers (all-MiniLM-L6-v2) or OpenAI
├── vectorstore.py FAISS per-workspace index on disk; Milvus adapter
└── retriever.py   similarity + MMR, metadata filters, score threshold
```
- **Index layout:** one FAISS index per workspace (`/data/vectors/{workspace_id}/`), metadata sidecar stores `{doc_id, source, chunk_no, text}`. Milvus adapter uses a single collection with a `workspace_id` partition key — flip `VECTOR_BACKEND=milvus`.
- **Why FAISS default:** zero-ops, fast for ≤ ~1M vectors/workspace. Milvus for horizontal scale.

## 5. Data model (PostgreSQL)
```
users ─┬─< workspace_members >─┬─ workspaces
       │                       ├─< documents (status, kind: pdf|docx|pptx|web|youtube)
       │                       ├─< conversations ─< messages
       │                       ├─< invoices (json extracted fields)
       │                       ├─< meetings (transcript, summary, action_items)
       │                       ├─< reports
       │                       └─< kb_articles
jobs (celery task mirror: id, type, status, result, error)
```
All FKs indexed; `messages` partitioned-ready by conversation; JSONB for extracted/flexible payloads.

## 6. Cross-cutting concerns
- **Auth:** JWT access (30 min) + refresh (14 d); bcrypt; role per workspace (owner/admin/member).
- **Rate limiting:** Redis sliding window per user (`core/ratelimit.py`), 60 req/min default, LLM routes 20/min.
- **Caching:** Redis — embeddings cache (sha256(text)→vector), website scrape cache (24 h TTL), YouTube transcript cache.
- **Streaming:** SSE (`text/event-stream`) for all LLM responses; mobile falls back to full-response mode.
- **Observability:** structured JSON logs (request id), `/health` + `/health/deep` (checks DB/Redis), Prometheus-ready middleware hooks.
- **Push notifications:** FCM tokens stored per device; Celery tasks notify on job completion.
- **Security:** file-type sniffing on upload, size caps, per-workspace storage quotas, prompt-injection hardening on scraped/web content (content wrapped as untrusted data in prompts).

## 7. Scaling path
| Concern | Now | Scale-up |
|---|---|---|
| API | 1 uvicorn container | N replicas behind Nginx/LB (stateless) |
| Workers | 1 celery, all queues | dedicated queues: `q.ocr`, `q.audio`, `q.ingest` w/ autoscale |
| Vectors | FAISS on volume | Milvus cluster (`VECTOR_BACKEND=milvus`) |
| LLM | OpenAI API | vLLM pool behind the same provider interface |
| DB | single Postgres | read replicas; pgbouncer |
| Files | local volume | S3-compatible (adapter in `services/storage.py`) |
