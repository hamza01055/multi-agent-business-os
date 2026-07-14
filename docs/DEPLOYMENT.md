# Deployment

## Local (Docker Compose)
```bash
cp .env.example .env
docker compose up --build
# API:   http://localhost:8080/docs
# Flower (optional): add profile `--profile debug`
```

## Environment
| Var | Purpose |
|---|---|
| `LLM_PROVIDER` | `openai` or `local` |
| `OPENAI_API_KEY` | when provider=openai |
| `LOCAL_LLM_BASE_URL` | OpenAI-compatible endpoint (Ollama/vLLM) |
| `VECTOR_BACKEND` | `faiss` (default) or `milvus` |
| `DATABASE_URL` / `REDIS_URL` | infra |
| `SECRET_KEY` | JWT signing |

## Production checklist
- TLS at Nginx (or a cloud LB); HSTS
- `SECRET_KEY` from a secret manager; rotate
- Postgres managed instance + backups; run `alembic upgrade head`
- Separate Celery queues (`ocr`, `audio`, `ingest`, `agents`) with per-queue concurrency
- Object storage (S3) for uploads via `services/storage.py`
- Horizontal API replicas: `docker compose up --scale api=3`

## Mobile
```bash
cd mobile && flutter pub get
flutter run --dart-define=API_BASE_URL=https://your-host/api/v1
```
