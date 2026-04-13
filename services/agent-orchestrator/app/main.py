"""Agent Orchestrator FastAPI application."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.routes import router
from .core.config import settings
from .tools.service_tools import service_client


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifecycle manager."""
    print(f"Starting {settings.SERVICE_NAME} on port {settings.SERVICE_PORT}")
    print(f"LLM Model: {settings.OPENAI_MODEL}")
    print(f"Sentinel enabled: {settings.ENABLE_SENTINEL}")
    yield
    # Cleanup
    await service_client.close()
    print(f"Shutting down {settings.SERVICE_NAME}")


app = FastAPI(
    title="Naql.ai Agent Orchestrator",
    description="LangGraph-powered AI agent for autonomous logistics orchestration",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.SERVICE_NAME}
