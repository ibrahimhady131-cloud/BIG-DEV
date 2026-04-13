"""GraphQL Gateway FastAPI application."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from .graphql.schema import schema


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifecycle manager."""
    print("Starting Naql.ai GraphQL Gateway on port 4000")
    yield
    print("Shutting down GraphQL Gateway")


app = FastAPI(
    title="Naql.ai GraphQL Gateway",
    description="Unified GraphQL API for the Naql.ai logistics ecosystem",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware for mobile/web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure per environment in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount GraphQL endpoint
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "graphql-gateway"}
