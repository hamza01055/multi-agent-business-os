from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import User, Document
from app.schemas.modules import WebsiteIngestIn
from app.schemas.chat import ChatQuestion
from app.core.deps import get_current_user
from app.api.v1.endpoints.workspaces import require_member
from app.services.rag.retriever import answer
from app.workers.tasks.ingest import ingest_website

router = APIRouter(prefix="/website", tags=["website-chat"])


@router.post("/ingest", status_code=202)
async def ingest(body: WebsiteIngestIn, user: User = Depends(get_current_user),
                 db: AsyncSession = Depends(get_db)):
    await require_member(db, body.workspace_id, user.id)
    doc = Document(workspace_id=body.workspace_id, uploader_id=user.id,
                   kind="web", title=str(body.url), source=str(body.url))
    db.add(doc)
    await db.commit()
    ingest_website.delay(doc.id, str(body.url), body.max_pages)
    return {"id": doc.id, "status": doc.status}


@router.post("/{doc_id}/chat")
async def chat(doc_id: str, body: ChatQuestion,
               user: User = Depends(get_current_user),
               db: AsyncSession = Depends(get_db)):
    doc = await db.get(Document, doc_id)
    if not doc or doc.status != "READY":
        raise HTTPException(409, "Website not ingested yet")
    await require_member(db, doc.workspace_id, user.id)

    async def gen():
        async for token in answer(doc.workspace_id, body.question, doc_id=doc.id):
            yield {"event": "token", "data": token}
        yield {"event": "done", "data": ""}
    return EventSourceResponse(gen())
