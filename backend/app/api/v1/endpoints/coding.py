from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
from app.core.deps import get_current_user
from app.core.ratelimit import rate_limit
from app.schemas.modules import CodingIn
from app.agents.coding_agent import assist

router = APIRouter(prefix="/coding", tags=["coding-assistant"],
                   dependencies=[Depends(get_current_user), Depends(rate_limit(limit=20))])


@router.post("/assist")
async def coding_assist(body: CodingIn):
    async def gen():
        async for token in assist(body.task, body.code, body.language):
            yield {"event": "token", "data": token}
        yield {"event": "done", "data": ""}
    return EventSourceResponse(gen())
