"""OCR tasks: invoice → text → structured fields."""
from app.workers.celery_app import celery
from app.workers.db import WorkerSession
from app.db.models import Invoice
from app.services.ocr import extract_text
from app.agents.invoice_extractor import extract_invoice_fields


@celery.task
def process_invoice(invoice_id: str):
    with WorkerSession() as db:
        invoice = db.get(Invoice, invoice_id)
        try:
            raw = extract_text(invoice.file_path)
            invoice.raw_text = raw
            invoice.extracted = extract_invoice_fields(raw)
            invoice.status = "READY"
        except Exception as e:  # noqa: BLE001
            invoice.status, invoice.error = "FAILED", str(e)[:2000]
        db.commit()
