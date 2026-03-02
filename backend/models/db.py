from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from config import settings


class Base(DeclarativeBase):
    pass


engine = create_async_engine(settings.database_url, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    """Create pgvector extension, all tables, and seed sources on startup."""
    async with engine.begin() as conn:
        # pgvector extension must exist before creating vector columns
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        # Import all models so Base knows about them
        from models import article, event, event_article, source  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)

    # Seed default sources (idempotent — skips existing rows)
    from workers.db_utils import seed_sources
    async with SessionLocal() as session:
        await seed_sources(session)
