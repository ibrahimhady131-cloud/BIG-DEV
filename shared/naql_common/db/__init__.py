"""Database connection management for CockroachDB and TimescaleDB."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class DatabaseManager:
    """Manages async database connections for CockroachDB and TimescaleDB."""

    def __init__(self, dsn: str, *, pool_size: int = 20, max_overflow: int = 10) -> None:
        self.engine: AsyncEngine = create_async_engine(
            dsn,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,
            echo=False,
        )
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Yield a database session with automatic cleanup."""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def close(self) -> None:
        """Dispose of the engine connection pool."""
        await self.engine.dispose()


class CockroachDB(DatabaseManager):
    """CockroachDB connection manager for transactional data (Orders, Billing, Users)."""

    def __init__(self, dsn: str) -> None:
        super().__init__(dsn, pool_size=30, max_overflow=15)


class TimescaleDB(DatabaseManager):
    """TimescaleDB connection manager for time-series data (GPS, Telemetry, Sensors)."""

    def __init__(self, dsn: str) -> None:
        super().__init__(dsn, pool_size=25, max_overflow=10)
