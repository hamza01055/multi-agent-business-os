"""LLM structured extraction of invoice fields from OCR text, with validation."""
import json
from app.schemas.invoice import InvoiceFields
from app.services.llm import get_chat_model


def extract_invoice_fields(raw_text: str) -> dict:
    llm = get_chat_model(temperature=0)
    schema = json.dumps(InvoiceFields.model_json_schema(), indent=0)
    resp = llm.invoke([
        ("system", "Extract invoice data from OCR text. Reply with JSON ONLY matching this schema "
                   f"(no markdown fences):\n{schema}"),
        ("user", raw_text[:12000]),
    ])
    text = resp.content.strip().strip("`").removeprefix("json").strip()
    fields = InvoiceFields.model_validate_json(text)

    # sanity check: line items should roughly reconcile with subtotal
    if fields.line_items:
        items_sum = round(sum(i.amount for i in fields.line_items), 2)
        if fields.subtotal and abs(items_sum - fields.subtotal) > max(1.0, 0.02 * fields.subtotal):
            fields.subtotal = items_sum  # trust itemized sum
    return fields.model_dump()
