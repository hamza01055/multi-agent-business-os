from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import User, Report
from app.core.deps import get_current_user
from app.api.v1.endpoints.workspaces import require_member
from app.schemas.modules import ReportIn
from app.workers.tasks.agents import report_task

router = APIRouter(prefix="/reports", tags=["report-generator"])


@router.post("", status_code=202)
async def create_report(body: ReportIn, user: User = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    await require_member(db, body.workspace_id, user.id)
    report = Report(workspace_id=body.workspace_id, user_id=user.id, topic=body.topic)
    db.add(report)
    await db.commit()
    report_task.delay(report.id, body.template)
    return {"id": report.id, "status": report.status}


@router.get("/{report_id}")
async def get_report(report_id: str, user: User = Depends(get_current_user),
                     db: AsyncSession = Depends(get_db)):
    report = await db.get(Report, report_id)
    if not report:
        raise HTTPException(404, "Not found")
    await require_member(db, report.workspace_id, user.id)
    return {"id": report.id, "topic": report.topic, "status": report.status,
            "content_md": report.content_md, "error": report.error}
