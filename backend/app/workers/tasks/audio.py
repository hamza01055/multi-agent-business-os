"""Audio tasks: meeting transcription + summarization + push notification."""
from app.workers.celery_app import celery
from app.workers.db import WorkerSession
from app.db.models import Meeting, User
from app.services.speech import transcribe
from app.services.push import notify
from app.agents.meeting_summarizer import summarize_meeting


@celery.task
def transcribe_meeting(meeting_id: str):
    with WorkerSession() as db:
        meeting = db.get(Meeting, meeting_id)
        try:
            transcript = transcribe(meeting.audio_path)
            result = summarize_meeting(transcript)
            meeting.transcript = transcript
            meeting.summary = result.get("summary", "")
            meeting.action_items = result.get("action_items", [])
            meeting.status = "READY"
            user = db.get(User, meeting.uploader_id)
            notify(user.fcm_token if user else None,
                   "Meeting summary ready", meeting.title)
        except Exception as e:  # noqa: BLE001
            meeting.status, meeting.error = "FAILED", str(e)[:2000]
        db.commit()
