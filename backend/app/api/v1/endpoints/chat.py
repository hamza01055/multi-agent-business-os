from fastapi import APIRouter, Depends, HTTPException
from sse_starlette.sse import EventSourceResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import User, Conversation, Message
from app.schemas.chat import ConversationCreate, MessageIn, MessageOut
from app.core.deps import get_current_user
from app.core.ratelimit import rate_limit
from app.api.v1.endpoints.workspaces import require_member
from app.services import llm

router = APIRouter(prefix="/chat", tags=["chat"])
HISTORY_WINDOW = 20


@router.post("/conversations", status_code=201)
async def create_conversation(body: ConversationCreate,
                              user: User = Depends(get_current_user),
                              db: AsyncSession = Depends(get_db)):
    await require_member(db, body.workspace_id, user.id)
    conv = Conversation(workspace_id=body.workspace_id, user_id=user.id,
                        title=body.title, kind=body.kind)
    db.add(conv)
    await db.commit()
    return {"id": conv.id, "title": conv.title}


@router.get("/conversations/{conversation_id}", response_model=list[MessageOut])
async def history(conversation_id: str, user: User = Depends(get_current_user),
                  db: AsyncSession = Depends(get_db)):
    rows = await db.execute(select(Message)
                            .where(Message.conversation_id == conversation_id)
                            .order_by(Message.created_at))
    return list(rows.scalars())


@router.post("/conversations/{conversation_id}/messages",
             dependencies=[Depends(rate_limit(limit=20))])
async def send_message(conversation_id: str, body: MessageIn,
                       user: User = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):
    conv = await db.get(Conversation, conversation_id)
    if not conv or conv.user_id != user.id:
        raise HTTPException(404, "Conversation not found")

    db.add(Message(conversation_id=conversation_id, role="user", content=body.content))
    await db.commit()

    rows = await db.execute(select(Message)
                            .where(Message.conversation_id == conversation_id)
                            .order_by(Message.created_at.desc()).limit(HISTORY_WINDOW))
    past = list(reversed(list(rows.scalars())))
    prompt = [("system", "You are a helpful business assistant.")] + \
             [(m.role, m.content) for m in past]

    async def event_gen():
        full = []
        async for token in llm.stream_chat(prompt):
            full.append(token)
            yield {"event": "token", "data": token}
        db.add(Message(conversation_id=conversation_id, role="assistant",
                       content="".join(full)))
        await db.commit()
        yield {"event": "done", "data": ""}

    if body.stream:
        return EventSourceResponse(event_gen())
    content = await llm.complete(prompt)
    db.add(Message(conversation_id=conversation_id, role="assistant", content=content))
    await db.commit()
    return {"role": "assistant", "content": content}
