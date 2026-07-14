from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, workspaces, chat, documents, website, youtube, meetings,
    email_assistant, invoices, research, reports, coding, kb, workflows, jobs,
)

api_router = APIRouter()
for module in (auth, workspaces, chat, documents, website, youtube, meetings,
               email_assistant, invoices, research, reports, coding, kb,
               workflows, jobs):
    api_router.include_router(module.router)
