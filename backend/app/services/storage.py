"""Upload storage adapter (local volume now; S3-compatible later)."""
import os, uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.core.config import settings

ALLOWED = {".pdf", ".docx", ".pptx", ".png", ".jpg", ".jpeg", ".mp3", ".wav", ".m4a", ".mp4"}


async def save_upload(file: UploadFile, subdir: str) -> str:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED:
        raise HTTPException(400, f"File type {ext} not allowed")
    data = await file.read()
    if len(data) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, "File too large")
    directory = os.path.join(settings.UPLOAD_DIR, subdir)
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{uuid.uuid4().hex}{ext}")
    with open(path, "wb") as f:
        f.write(data)
    return path
