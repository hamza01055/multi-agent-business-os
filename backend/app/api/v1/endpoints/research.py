from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import User
from app.core.deps import get_current_user
from app.api.v1.endpoints.workspaces import require_member
from app.schemas.modules import ResearchIn
from app.schemas.common import JobOut
from app.workers.tasks.agents import research_task

router = APIRouter(prefix="/research", tags=["research-agent"])


@router.post("", response_model=JobOut, status_code=202)
async def start_research(body: ResearchIn, user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    await require_member(db, body.workspace_id, user.id)
    task = research_task.delay(body.workspace_id, body.question, body.depth)
    return JobOut(job_id=task.id)
