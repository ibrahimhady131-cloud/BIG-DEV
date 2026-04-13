"""FinTrack Service configuration."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """FinTrack service settings."""

    SERVICE_NAME: str = "fintrack-service"
    SERVICE_PORT: int = 8004
    GRPC_PORT: int = 50054
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://root@localhost:26257/naql_fintrack"
    NATS_URL: str = "nats://localhost:4222"
    REDIS_URL: str = "redis://localhost:6379/3"

    # Payment gateways
    FAWRY_API_KEY: str = ""
    FAWRY_SECRET: str = ""
    PAYMOB_API_KEY: str = ""
    PAYMOB_INTEGRATION_ID: str = ""

    # Pricing
    SERVICE_FEE_PERCENTAGE: float = 0.08  # 8% platform fee
    INSURANCE_RATE_PER_KM: float = 0.5  # EGP per km
    BASE_FUEL_RATE_PER_KM: float = 4.5  # EGP per km (diesel)

    model_config = {"env_prefix": "FINTRACK_", "env_file": ".env"}


settings = Settings()
