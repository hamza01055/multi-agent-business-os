from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import User, Workspace, WorkspaceMember
from app.core.deps import get_current_user

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


class WorkspaceCreateIn(BaseModel):
    name: str


class MemberAddIn(BaseModel):
    email: str
    role: str = "member"


async def require_member(db: AsyncSession, workspace_id: str, user_id: str) -> WorkspaceMember:
    m = await db.scalar(select(WorkspaceMember).where(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id))
    if not m:
        raise HTTPException(403, "Not a member of this workspace")
    return m


@router.post("", status_code=201)
async def create_workspace(body: WorkspaceCreateIn, user: User = Depends(get_current_user),
                           db: AsyncSession = Depends(get_db)):
    ws = Workspace(name=body.name, owner_id=user.id)
    db.add(ws)
    await db.flush()
    db.add(WorkspaceMember(workspace_id=ws.id, user_id=user.id, role="owner"))
    await db.commit()
    return {"id": ws.id, "name": ws.name}


@router.get("")
async def list_workspaces(user: User = Depends(get_current_user),
                          db: AsyncSession = Depends(get_db)):
    rows = await db.execute(
        select(Workspace).join(WorkspaceMember,
                               WorkspaceMember.workspace_id == Workspace.id)
        .where(WorkspaceMember.user_id == user.id))
    return [{"id": w.id, "name": w.name} for w in rows.scalars()]


@router.post("/{workspace_id}/members", status_code=201)
async def add_member(workspace_id: str, body: MemberAddIn,
                     user: User = Depends(get_current_user),
                     db: AsyncSession = Depends(get_db)):
    me = await require_member(db, workspace_id, user.id)
    if me.role not in ("owner", "admin"):
        raise HTTPException(403, "Only owners/admins can add members")
    target = await db.scalar(select(User).where(User.email == body.email))
    if not target:
        raise HTTPException(404, "User not found")
    db.add(WorkspaceMember(workspace_id=workspace_id, user_id=target.id, role=body.role))
    await db.commit()
    return {"detail": "added"}
