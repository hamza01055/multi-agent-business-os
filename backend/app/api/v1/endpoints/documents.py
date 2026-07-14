from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sse_starlette.sse import EventSourceResponse
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import User, Document
from app.schemas.chat import ChatQuestion
from app.core.deps import get_current_user
from app.api.v1.endpoints.workspaces import require_member
from app.services.storage import save_upload
from app.services.rag.retriever import answer
from app.workers.tasks.ingest import ingest_document

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", status_code=202)
async def upload_document(workspace_id: str = Form(...), file: UploadFile = File(...),
                          user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    await require_member(db, workspace_id, user.id)
    ext = Path(file.filename or "").suffix.lower().lstrip(".")
    if ext not in ("pdf", "docx", "pptx"):
        raise HTTPException(400, "Only PDF, DOCX, PPTX are supported here")
    path = await save_upload(file, f"docs/{workspace_id}")
    doc = Document(workspace_id=workspace_id, uploader_id=user.id, kind=ext,
                   title=file.filename or "document", source=path)
    db.add(doc)
    await db.commit()
    ingest_document.delay(doc.id)
    return {"id": doc.id, "status": doc.status}


@router.get("/{doc_id}")
async def get_document(doc_id: str, user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    doc = await db.get(Document, doc_id)
    if not doc:
        raise HTTPException(404, "Not found")
    await require_member(db, doc.workspace_id, user.id)
    return {"id": doc.id, "title": doc.title, "kind": doc.kind,
            "status": doc.status, "chunk_count": doc.chunk_count, "error": doc.error}


@router.post("/{doc_id}/chat")
async def chat_with_document(doc_id: str, body: ChatQuestion,
                             user: User = Depends(get_current_user),
                             db: AsyncSession = Depends(get_db)):
    doc = await db.get(Document, doc_id)
    if not doc or doc.status != "READY":
        raise HTTPException(409, "Document not ready")
    await require_member(db, doc.workspace_id, user.id)

    async def gen():
        async for token in answer(doc.workspace_id, body.question, doc_id=doc.id):
            yield {"event": "token", "data": token}
        yield {"event": "done", "data": ""}
    return EventSourceResponse(gen())
