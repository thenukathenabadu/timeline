from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.db import init_db
from api.routes import health, events, articles, sources, admin
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Timeline API",
    description="Backend for the Timeline global event timeline website",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(events.router, prefix="/api/v1", tags=["events"])
app.include_router(articles.router, prefix="/api/v1", tags=["articles"])
app.include_router(sources.router, prefix="/api/v1", tags=["sources"])
app.include_router(admin.router, prefix="/api/v1", tags=["admin"])
