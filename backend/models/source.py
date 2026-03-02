import uuid
from datetime import datetime
from sqlalchemy import String, Text, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from models.db import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)  # e.g. "bbc", "reuters"
    display_name: Mapped[str] = mapped_column(String(100))
    url: Mapped[str | None] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    last_scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
