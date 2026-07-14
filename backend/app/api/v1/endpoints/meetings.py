from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import User, Meeting
from app.core.deps import get_current_user
from app.api.v1.endpoints.workspaces import require_member
from app.services.storage import save_upload
from app.workers.tasks.audio import transcribe_meeting

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.post("", status_code=202)
async def upload_meeting(workspace_id: str = Form(...), title: str = Form("Meeting"),
                         file: UploadFile = File(...),
                         user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    await require_member(db, workspace_id, user.id)
    path = await save_upload(file, f"meetings/{workspace_id}")
    meeting = Meeting(workspace_id=workspace_id, uploader_id=user.id,
                      title=title, audio_path=path)
    db.add(meeting)
    await db.commit()
    transcribe_meeting.delay(meeting.id)
    return {"id": meeting.id, "status": meeting.status}


@router.get("/{meeting_id}")
async def get_meeting(meeting_id: str, user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        raise HTTPException(404, "Not found")
    await require_member(db, meeting.workspace_id, user.id)
    return {"id": meeting.id, "title": meeting.title, "status": meeting.status,
            "transcript": meeting.transcript, "summary": meeting.summary,
            "action_items": meeting.action_items, "error": meeting.error}
