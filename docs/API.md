# API Reference (summary)

Base URL: `http://localhost:8080/api/v1` · Auth: `Authorization: Bearer <JWT>` · Interactive docs: `/docs`

## Auth
- `POST /auth/register` {email, password, full_name}
- `POST /auth/login` → {access_token, refresh_token}
- `POST /auth/refresh`

## Workspaces
- `POST /workspaces` · `GET /workspaces` · `POST /workspaces/{id}/members`

## Chat
- `POST /chat/conversations` → conversation
- `POST /chat/conversations/{id}/messages` {content, stream=true} → SSE tokens
- `GET  /chat/conversations/{id}` history

## Documents (PDF/DOCX/PPTX)
- `POST /documents` multipart → {id, status:PENDING}
- `GET  /documents/{id}` status → READY
- `POST /documents/{id}/chat` {question} → answer + citations

## Website & YouTube chat
- `POST /website/ingest` {url} → job · `POST /website/{id}/chat`
- `POST /youtube/ingest` {video_url} · `POST /youtube/{id}/chat`

## Meetings
- `POST /meetings` (audio multipart) → job
- `GET  /meetings/{id}` → {transcript, summary, action_items}

## Email assistant
- `POST /email/draft` {intent, context, tone} → {subject, body, variants[]}
- `POST /email/reply` {thread, instruction}

## Invoices
- `POST /invoices` (pdf/image) → job → `GET /invoices/{id}` structured fields

## Agents
- `POST /research` {question, depth} → job → cited report
- `POST /reports` {topic, template, data_sources[]} → job → markdown/pdf
- `POST /coding/assist` {task, code?, language?} → streamed answer
- `POST /workflows/run` {task} → multi-agent trace + result

## Knowledge base
- `POST /kb/articles` · `GET /kb/search?q=` (workspace-scoped semantic search)

## Jobs
- `GET /jobs/{id}` → {status: pending|started|success|failure, result}
