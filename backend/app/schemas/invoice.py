from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str
    quantity: float = 1
    unit_price: float = 0
    amount: float = 0


class InvoiceFields(BaseModel):
    """Target schema for LLM structured extraction from OCR text."""
    vendor: str = ""
    invoice_number: str = ""
    invoice_date: str = ""
    due_date: str = ""
    currency: str = "USD"
    line_items: list[LineItem] = Field(default_factory=list)
    subtotal: float = 0
    tax: float = 0
    total: float = 0
