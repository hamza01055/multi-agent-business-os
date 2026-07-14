from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey
from app.db.base import Base, TimestampMixin, uid


class Document(Base, TimestampMixin):
    """Any RAG source: uploaded file, website, or YouTube video."""
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=uid)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"), index=True)
    uploader_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    kind: Mapped[str] = mapped_column(String(20))  # pdf|docx|pptx|web|youtube|kb
    title: Mapped[str] = mapped_column(String(500))
    source: Mapped[str] = mapped_column(String(1000))  # file path or URL
    status: Mapped[str] = mapped_column(String(20), default="PENDING")  # PENDING|READY|FAILED
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(String(2000), nullable=True)
