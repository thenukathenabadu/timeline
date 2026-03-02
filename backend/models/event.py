import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column
from models.db import Base


class Event(Base):
    """
    A real-world occurrence linked to one or more Articles from different sources.
    The timeline renders Events; the side panel shows all linked Articles.
    """
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)

    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    category: Mapped[str | None] = mapped_column(String(50))
    country_codes: Mapped[list[str] | None] = mapped_column(ARRAY(String(3)))

    # True when linked articles disagree on timing or key facts
    has_conflict: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
