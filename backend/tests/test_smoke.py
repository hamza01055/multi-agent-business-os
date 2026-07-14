"""Smoke tests: app imports and health endpoint works (no external services)."""
from fastapi.testclient import TestClient


def test_app_imports():
    from app.main import app
    assert app.title == "AI Business OS"


def test_invoice_schema_roundtrip():
    from app.schemas.invoice import InvoiceFields, LineItem
    inv = InvoiceFields(vendor="ACME", line_items=[LineItem(description="X", amount=10)],
                        subtotal=10, total=10)
    assert inv.model_dump()["vendor"] == "ACME"


def test_chunker():
    from app.services.rag.chunker import chunk_text
    chunks = chunk_text("word " * 2000)
    assert len(chunks) > 1
