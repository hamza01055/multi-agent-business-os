from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.deps import get_current_user
from app.core.ratelimit import rate_limit
from app.schemas.modules import EmailDraftIn
from app.agents.email_agent import draft_email, reply_email

router = APIRouter(prefix="/email", tags=["email-assistant"],
                   dependencies=[Depends(get_current_user), Depends(rate_limit(limit=20))])


class ReplyIn(BaseModel):
    thread: str
    instruction: str


@router.post("/draft")
async def draft(body: EmailDraftIn):
    variants = [await draft_email(body.intent, body.context, body.tone)
                for _ in range(max(1, body.variants))]
    return {"subject": variants[0]["subject"], "body": variants[0]["body"],
            "variants": variants}


@router.post("/reply")
async def reply(body: ReplyIn):
    return await reply_email(body.thread, body.instruction)
