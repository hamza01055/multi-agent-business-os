from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import User, Document
from app.core.deps import get_current_user
from app.api.v1.endpoints.workspaces import require_member
from app.schemas.modules import KBArticleIn
from app.services.rag.vectorstore import similarity_search
from app.workers.tasks.ingest import ingest_kb_article

router = APIRouter(prefix="/kb", tags=["knowledge-base"])


@router.post("/articles", status_code=202)
async def add_article(body: KBArticleIn, user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    await require_member(db, body.workspace_id, user.id)
    doc = Document(workspace_id=body.workspace_id, uploader_id=user.id,
                   kind="kb", title=body.title, source="kb")
    db.add(doc)
    await db.commit()
    ingest_kb_article.delay(doc.id, f"{body.title}\n\n{body.content}")
    return {"id": doc.id, "status": doc.status}


@router.get("/search")
async def search(workspace_id: str, q: str, k: int = 5,
                 user: User = Depends(get_current_user),
                 db: AsyncSession = Depends(get_db)):
    await require_member(db, workspace_id, user.id)
    docs = similarity_search(workspace_id, q, k=k)
    return [{"text": d.page_content, "source": d.metadata.get("source"),
             "doc_id": d.metadata.get("doc_id")} for d in docs]
