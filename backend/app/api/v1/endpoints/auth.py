from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import User, Workspace, WorkspaceMember
from app.schemas.auth import RegisterIn, TokenOut, UserOut, RefreshIn, FcmTokenIn
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
)
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
async def register(body: RegisterIn, db: AsyncSession = Depends(get_db)):
    exists = await db.scalar(select(User).where(User.email == body.email))
    if exists:
        raise HTTPException(409, "Email already registered")
    user = User(email=body.email, full_name=body.full_name,
                hashed_password=hash_password(body.password))
    db.add(user)
    await db.flush()
    ws = Workspace(name=f"{body.full_name or body.email}'s workspace", owner_id=user.id)
    db.add(ws)
    await db.flush()
    db.add(WorkspaceMember(workspace_id=ws.id, user_id=user.id, role="owner"))
    await db.commit()
    return user


@router.post("/login", response_model=TokenOut)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await db.scalar(select(User).where(User.email == form.username))
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(401, "Incorrect email or password")
    return TokenOut(access_token=create_access_token(user.id),
                    refresh_token=create_refresh_token(user.id))


@router.post("/refresh", response_model=TokenOut)
async def refresh(body: RefreshIn):
    user_id = decode_token(body.refresh_token, expect="refresh")
    if not user_id:
        raise HTTPException(401, "Invalid refresh token")
    return TokenOut(access_token=create_access_token(user_id),
                    refresh_token=create_refresh_token(user_id))


@router.get("/me", response_model=UserOut)
async def me(user: User = Depends(get_current_user)):
    return user


@router.post("/fcm-token")
async def set_fcm_token(body: FcmTokenIn, user: User = Depends(get_current_user),
                        db: AsyncSession = Depends(get_db)):
    user.fcm_token = body.token
    db.add(user)
    await db.commit()
    return {"detail": "ok"}
