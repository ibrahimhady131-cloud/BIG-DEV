"""Telemetry Ingress FastAPI application."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from naql_common.db.deps import close_all, init_timescale

from .core.config import settings
from .processing.processor import MessageProcessor

processor = MessageProcessor(batch_size=settings.BATCH_SIZE)

api_router = APIRouter(prefix="/api/v1", tags=["telemetry"])


@api_router.post("/ingest/position")
async def ingest_position(payload: dict) -> dict:
    """HTTP fallback for position ingestion (primary is MQTT)."""
    from .processing.processor import PositionMessage

    msg = PositionMessage(
        truck_id=payload["truck_id"],
        driver_id=payload.get("driver_id"),
        trip_id=payload.get("trip_id"),
        latitude=payload["latitude"],
        longitude=payload["longitude"],
        altitude_m=payload.get("altitude_m"),
        speed_kmh=payload.get("speed_kmh", 0.0),
        heading=payload.get("heading"),
        signal_strength=payload.get("signal_strength"),
        connection_type=payload.get("connection_type"),
        ignition_on=payload.get("ignition_on", True),
    )

    events = processor.process_position(msg)

    return {
        "received": True,
        "events_generated": len(events),
        "events": events,
        "buffer_size": processor.position_buffer_size,
    }


@api_router.post("/ingest/telemetry")
async def ingest_telemetry(payload: dict) -> dict:
    """HTTP fallback for telemetry ingestion (primary is MQTT)."""
    from .processing.processor import TelemetryMessage

    msg = TelemetryMessage(
        truck_id=payload["truck_id"],
        engine_rpm=payload.get("engine_rpm"),
        engine_temp_c=payload.get("engine_temp_c"),
        fuel_level_pct=payload.get("fuel_level_pct"),
        fuel_rate_lph=payload.get("fuel_rate_lph"),
        odometer_km=payload.get("odometer_km"),
        battery_voltage=payload.get("battery_voltage"),
        cargo_temp_c=payload.get("cargo_temp_c"),
        harsh_braking=payload.get("harsh_braking", False),
        harsh_acceleration=payload.get("harsh_acceleration", False),
        sharp_turn=payload.get("sharp_turn", False),
    )

    events = processor.process_telemetry(msg)

    return {
        "received": True,
        "events_generated": len(events),
        "events": events,
        "buffer_size": processor.telemetry_buffer_size,
    }


@api_router.get("/telemetry/stats")
async def get_stats() -> dict:
    """Get current telemetry processing statistics."""
    return {
        "position_buffer_size": processor.position_buffer_size,
        "telemetry_buffer_size": processor.telemetry_buffer_size,
    }


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifecycle manager."""
    print(f"Starting {settings.SERVICE_NAME} on port {settings.SERVICE_PORT}")
    print(f"MQTT Broker: {settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}")
    if settings.TIMESCALE_URL and settings.TIMESCALE_URL != "sqlite://":
        try:
            init_timescale(settings.TIMESCALE_URL)
            print(f"  Connected to TimescaleDB: {settings.TIMESCALE_URL.split('@')[-1]}")
        except Exception as e:
            print(f"  WARNING: TimescaleDB not available ({e}), using in-memory buffer")
    else:
        print("  Using in-memory buffer (no TIMESCALE_URL configured)")
    yield
    await close_all()
    print(f"Shutting down {settings.SERVICE_NAME}")


app = FastAPI(
    title="Naql.ai Telemetry Ingress",
    description="MQTT telemetry ingestion and real-time stream processing",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(api_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": settings.SERVICE_NAME}
