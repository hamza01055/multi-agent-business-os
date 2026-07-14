from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import User
from app.core.deps import get_current_user
from app.core.ratelimit import rate_limit
from app.api.v1.endpoints.workspaces import require_member
from app.schemas.modules import WorkflowIn
from app.agents.multi_agent import run_workflow

router = APIRouter(prefix="/workflows", tags=["multi-agent"],
                   dependencies=[Depends(rate_limit(limit=10))])


@router.post("/run")
async def run(body: WorkflowIn, user: User = Depends(get_current_user),
              db: AsyncSession = Depends(get_db)):
    await require_member(db, body.workspace_id, user.id)
    return await run_in_threadpool(run_workflow, body.workspace_id, body.task)
