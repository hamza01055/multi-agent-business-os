from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import User, Invoice
from app.core.deps import get_current_user
from app.api.v1.endpoints.workspaces import require_member
from app.services.storage import save_upload
from app.workers.tasks.ocr import process_invoice

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("", status_code=202)
async def upload_invoice(workspace_id: str = Form(...), file: UploadFile = File(...),
                         user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    await require_member(db, workspace_id, user.id)
    path = await save_upload(file, f"invoices/{workspace_id}")
    invoice = Invoice(workspace_id=workspace_id, uploader_id=user.id, file_path=path)
    db.add(invoice)
    await db.commit()
    process_invoice.delay(invoice.id)
    return {"id": invoice.id, "status": invoice.status}


@router.get("/{invoice_id}")
async def get_invoice(invoice_id: str, user: User = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    invoice = await db.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(404, "Not found")
    await require_member(db, invoice.workspace_id, user.id)
    return {"id": invoice.id, "status": invoice.status,
            "extracted": invoice.extracted, "error": invoice.error}
