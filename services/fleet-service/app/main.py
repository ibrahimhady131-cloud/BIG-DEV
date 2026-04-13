"""Fleet Service FastAPI application."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from naql_common.db.deps import close_all, init_cockroach

from .api.routes import router
from .core.config import settings


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifecycle manager."""
    print(f"Starting {settings.SERVICE_NAME} on port {settings.SERVICE_PORT}")
    if settings.DATABASE_URL and settings.DATABASE_URL != "sqlite://":
        try:
            init_cockroach(settings.DATABASE_URL)
            print(f"  Connected to CockroachDB: {settings.DATABASE_URL.split('@')[-1]}")
        except Exception as e:
            print(f"  WARNING: CockroachDB not available ({e}), using in-memory store")
    else:
        print("  Using in-memory store (no DATABASE_URL configured)")
    yield
    await close_all()
    print(f"Shutting down {settings.SERVICE_NAME}")


app = FastAPI(
    title="Naql.ai Fleet Service",
    description="Fleet management, truck lifecycle, and maintenance tracking",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.SERVICE_NAME}
