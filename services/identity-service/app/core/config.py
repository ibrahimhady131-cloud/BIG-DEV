"""Identity Service configuration."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Identity service settings loaded from environment variables."""

    # Service
    SERVICE_NAME: str = "identity-service"
    SERVICE_PORT: int = 8001
    GRPC_PORT: int = 50051
    DEBUG: bool = False

    # Database (CockroachDB)
    DATABASE_URL: str = "postgresql+asyncpg://root@localhost:26257/naql_identity"

    # Auth
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # NATS
    NATS_URL: str = "nats://localhost:4222"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = {"env_prefix": "IDENTITY_", "env_file": ".env"}


settings = Settings()
