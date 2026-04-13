"""FinTrack Service FastAPI application."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.routes import router
from .core.config import settings


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifecycle manager."""
    print(f"Starting {settings.SERVICE_NAME} on port {settings.SERVICE_PORT}")
    yield
    print(f"Shutting down {settings.SERVICE_NAME}")


app = FastAPI(
    title="Naql.ai FinTrack Service",
    description="Financial ledger, payments, escrow, and pricing engine",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.SERVICE_NAME}
