"""Database initialization script — creates all tables in Replit PostgreSQL.

Run with:  python scripts/init_db.py
"""

from __future__ import annotations

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

from naql_common.db import _normalize_dsn
from naql_common.db.base import Base

# Import all models so SQLAlchemy registers them
from naql_common.db.models.fintrack import EscrowHold, LedgerAccount, Transaction
from naql_common.db.models.fleet import Truck, TruckMaintenance
from naql_common.db.models.identity import ApiKey, User, UserDocument
from naql_common.db.models.notification import Notification
from naql_common.db.models.shipment import (
    DriverPreferences,
    MatchHistory,
    Shipment,
    ShipmentAuditLog,
    Trip,
)
from naql_common.db.models.telemetry import DrivingViolation, GeofenceEvent

from sqlalchemy.ext.asyncio import create_async_engine

# Telemetry models need regular Postgres (not TimescaleDB hypertable setup here)
# TruckPosition and TruckTelemetry require TimescaleDB extensions — skip for now
# from naql_common.db.models.telemetry import TruckPosition, TruckTelemetry


async def init_db() -> None:
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL environment variable not set")
        sys.exit(1)

    normalized_url, connect_args = _normalize_dsn(db_url)
    print(f"Connecting to: {normalized_url.split('@')[-1]}")

    engine = create_async_engine(
        normalized_url,
        connect_args=connect_args,
        echo=False,
    )

    async with engine.begin() as conn:
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("Done.")

    await engine.dispose()

    # Verify key tables
    from sqlalchemy import text
    engine2 = create_async_engine(normalized_url, connect_args=connect_args)
    async with engine2.connect() as conn:
        result = await conn.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename")
        )
        tables = [row[0] for row in result.fetchall()]
        print(f"\nTables in database ({len(tables)} total):")
        for t in tables:
            print(f"  ✓ {t}")
    await engine2.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
