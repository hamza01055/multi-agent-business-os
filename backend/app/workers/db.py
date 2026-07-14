"""Sync DB session for Celery workers (workers don't share the async loop)."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.SYNC_DATABASE_URL, pool_pre_ping=True)
WorkerSession = sessionmaker(engine)
