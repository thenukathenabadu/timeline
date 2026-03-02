from fastapi import APIRouter
from sqlalchemy import text
from models.db import SessionLocal

router = APIRouter()


@router.get("/health")
async def health():
    """Basic health check. Also verifies DB connectivity."""
    try:
        async with SessionLocal() as session:
            await session.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:
        db_status = f"error: {exc}"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "database": db_status,
    }
