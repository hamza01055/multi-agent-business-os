"""Ingestion tasks: file / website / youtube → chunks → workspace vector index."""
from app.workers.celery_app import celery
from app.workers.db import WorkerSession
from app.db.models import Document
from app.services.rag.loaders import load_file
from app.services.rag.chunker import chunk_text
from app.services.rag.vectorstore import upsert_chunks
from app.services.scraper import scrape
from app.services.youtube import get_transcript


def _ingest_text(doc_id: str, text: str):
    with WorkerSession() as db:
        doc = db.get(Document, doc_id)
        try:
            chunks = chunk_text(text)
            n = upsert_chunks(doc.workspace_id, doc.id, doc.title, chunks)
            doc.status, doc.chunk_count = "READY", n
        except Exception as e:  # noqa: BLE001
            doc.status, doc.error = "FAILED", str(e)[:2000]
        db.commit()


@celery.task
def ingest_document(doc_id: str):
    with WorkerSession() as db:
        doc = db.get(Document, doc_id)
        path = doc.source
    _ingest_text(doc_id, load_file(path))


@celery.task
def ingest_website(doc_id: str, url: str, max_pages: int = 5):
    _ingest_text(doc_id, scrape(url, max_pages))


@celery.task
def ingest_youtube(doc_id: str, video_url: str):
    _ingest_text(doc_id, get_transcript(video_url))


@celery.task
def ingest_kb_article(doc_id: str, content: str):
    _ingest_text(doc_id, content)
