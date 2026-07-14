from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, JSON
from app.db.base import Base, TimestampMixin, uid


class Invoice(Base, TimestampMixin):
    __tablename__ = "invoices"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    uploader_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    file_path: Mapped[str] = mapped_column(String(1000))
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    raw_text: Mapped[str | None] = mapped_column(String, nullable=True)
    extracted: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # vendor, totals, line_items...
    error: Mapped[str | None] = mapped_column(String(2000), nullable=True)
