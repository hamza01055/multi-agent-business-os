from celery import Celery
from app.core.config import settings

celery = Celery(
    "aibos",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.tasks.ingest",
        "app.workers.tasks.audio",
        "app.workers.tasks.ocr",
        "app.workers.tasks.agents",
    ],
)
celery.conf.update(
    task_routes={
        "app.workers.tasks.ingest.*": {"queue": "ingest"},
        "app.workers.tasks.audio.*": {"queue": "audio"},
        "app.workers.tasks.ocr.*": {"queue": "ocr"},
        "app.workers.tasks.agents.*": {"queue": "agents"},
    },
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_time_limit=1800,
)
