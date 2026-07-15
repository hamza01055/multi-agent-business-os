# AI Business OS — AI Business Operating System

> Not just another chatbot — a production-grade AI platform that automates business work
> using multiple cooperating AI agents, RAG, OCR, speech, and workflow automation.

![Python](https://img.shields.io/badge/Python-3.11-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green) ![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B) ![LangGraph](https://img.shields.io/badge/LangGraph-agents-orange) ![Docker](https://img.shields.io/badge/Docker-compose-2496ED)

## Why it stands out
- Combines **LLMs, RAG, agents, OCR, speech, and automation** in one coherent architecture
- **Production-level architecture**: async FastAPI, Celery workers, Redis, PostgreSQL, Nginx, Docker
- Provider-agnostic LLM layer (**OpenAI or local LLM** via one config switch)
- Multi-tenant **team workspaces** with a shared knowledge base
- Full **Flutter mobile app** with voice, offline cache, and push notifications


## Modules
| Module | Endpoint | Core tech |
|---|---|---|
| AI Chat | `/api/v1/chat` | LLM + memory |
| Document Chat (PDF/DOCX/PPTX) | `/api/v1/documents` | Loaders → chunks → FAISS RAG |
| Website Chat | `/api/v1/website` | Scraper → RAG |
| YouTube Video Chat | `/api/v1/youtube` | Transcript → RAG |
| Meeting Summarizer | `/api/v1/meetings` | Whisper → LLM summary (Celery) |
| Email Assistant | `/api/v1/email` | LLM drafting agent |
| Invoice Reader (OCR) | `/api/v1/invoices` | Tesseract OCR → structured extraction |
| AI Research Agent | `/api/v1/research` | LangGraph plan→search→synthesize |
| AI Report Generator | `/api/v1/reports` | Agent + templating (Celery) |
| AI Coding Assistant | `/api/v1/coding` | Code-tuned prompting |
| Team Knowledge Base | `/api/v1/kb` | Workspace-scoped vector store |
| Multi-Agent Workflow | `/api/v1/workflows` | LangGraph supervisor + workers |

## Quick start
```bash
cp .env.example .env          # add your OPENAI_API_KEY (or set LLM_PROVIDER=local)
docker compose up --build     # api → http://localhost:8080  docs → /docs
```

## Repository layout
```
ai-business-os/
├── backend/           FastAPI app, agents, RAG, Celery workers
├── mobile/            Flutter app (chat, voice, files, workspaces)
├── nginx/             Reverse proxy config
├── docs/              Architecture, API, deployment docs
├── scripts/           Dev helpers & DB seed
└── docker-compose.yml Postgres + Redis + API + Worker + Nginx
```

## Architecture (high level)
```
 Flutter App ──HTTPS──▶ Nginx ──▶ FastAPI (async)
                                   │
              ┌────────────────────┼─────────────────────┐
              ▼                    ▼                     ▼
        PostgreSQL             Redis (cache,        Celery Workers
        (users, docs,          broker, rate         (OCR, Whisper,
        chats, invoices)       limits, pubsub)      ingest, reports)
                                   │
                                   ▼
                     AI Layer: LangGraph agents → LangChain →
                     LLM Provider (OpenAI | local) + FAISS/Milvus
                     + Sentence-Transformers + Whisper + Tesseract
```
See **docs/ARCHITECTURE.md** for the full deep-dive (data flow, agent graphs, scaling).

## License
MIT

