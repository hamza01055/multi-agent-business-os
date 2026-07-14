"""Seed a demo user + workspace. Run inside the api container:
   docker compose exec api python scripts/seed.py
"""
import asyncio
from app.db.session import SessionLocal
from app.db.models import User, Workspace, WorkspaceMember
from app.core.security import hash_password


async def main():
    async with SessionLocal() as db:
        user = User(email="demo@aibos.dev", full_name="Demo User",
                    hashed_password=hash_password("demo1234"))
        db.add(user)
        await db.flush()
        ws = Workspace(name="Demo Workspace", owner_id=user.id)
        db.add(ws)
        await db.flush()
        db.add(WorkspaceMember(workspace_id=ws.id, user_id=user.id, role="owner"))
        await db.commit()
        print(f"Seeded demo@aibos.dev / demo1234 — workspace {ws.id}")


if __name__ == "__main__":
    asyncio.run(main())
