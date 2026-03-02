import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from models.db import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("sources.id"), nullable=False
    )
    url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)

    # SHA-256 of (title + published_at) — prevents duplicate inserts
    content_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)

    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # AI-extracted event date (may differ from published_at)
    event_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # AI classification
    category: Mapped[str | None] = mapped_column(String(50))
    country_codes: Mapped[list[str] | None] = mapped_column(ARRAY(String(3)))

    # 384-dim embedding from all-MiniLM-L6-v2
    embedding: Mapped[list[float] | None] = mapped_column(Vector(384))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
