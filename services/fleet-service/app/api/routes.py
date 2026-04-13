"""Fleet Service API routes."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status

from ..schemas.truck import (
    MaintenanceRequest,
    MaintenanceResponse,
    TruckListResponse,
    TruckRegisterRequest,
    TruckResponse,
    TruckStatusUpdateRequest,
)

router = APIRouter(prefix="/api/v1", tags=["fleet"])

# In-memory store for demo
_trucks_db: dict[str, dict] = {}
_maintenance_db: dict[str, dict] = {}


@router.post("/trucks", response_model=TruckResponse, status_code=status.HTTP_201_CREATED)
async def register_truck(request: TruckRegisterRequest) -> TruckResponse:
    """Register a new truck in the fleet."""
    # Check for duplicate license plate
    for truck in _trucks_db.values():
        if truck["license_plate"] == request.license_plate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="License plate already registered",
            )

    truck_id = str(uuid.uuid4())
    truck_data = {
        "id": truck_id,
        **request.model_dump(),
        "status": "offline",
        "has_gps_tracker": True,
        "created_at": datetime.now(UTC),
    }
    _trucks_db[truck_id] = truck_data

    return TruckResponse(**truck_data)


@router.get("/trucks/{truck_id}", response_model=TruckResponse)
async def get_truck(truck_id: str) -> TruckResponse:
    """Get truck details by ID."""
    truck = _trucks_db.get(truck_id)
    if truck is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Truck not found")
    return TruckResponse(**truck)


@router.patch("/trucks/{truck_id}/status", response_model=TruckResponse)
async def update_truck_status(truck_id: str, request: TruckStatusUpdateRequest) -> TruckResponse:
    """Update a truck's operational status."""
    truck = _trucks_db.get(truck_id)
    if truck is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Truck not found")

    truck["status"] = request.status
    return TruckResponse(**truck)


@router.get("/trucks", response_model=TruckListResponse)
async def list_trucks(
    page: int = 1,
    page_size: int = 20,
    truck_type: str | None = None,
    status_filter: str | None = None,
    region_code: str | None = None,
) -> TruckListResponse:
    """List trucks with pagination and filtering."""
    trucks = list(_trucks_db.values())

    if truck_type:
        trucks = [t for t in trucks if t["truck_type"] == truck_type]
    if status_filter:
        trucks = [t for t in trucks if t["status"] == status_filter]
    if region_code:
        trucks = [t for t in trucks if t["region_code"] == region_code]

    total = len(trucks)
    start = (page - 1) * page_size
    end = start + page_size
    page_trucks = trucks[start:end]

    return TruckListResponse(
        trucks=[TruckResponse(**t) for t in page_trucks],
        total=total,
        page=page,
        page_size=page_size,
        has_next=end < total,
    )


@router.get("/trucks/owner/{owner_id}", response_model=TruckListResponse)
async def get_trucks_by_owner(
    owner_id: str, page: int = 1, page_size: int = 20
) -> TruckListResponse:
    """Get all trucks owned by a specific user."""
    trucks = [t for t in _trucks_db.values() if t["owner_id"] == owner_id]
    total = len(trucks)
    start = (page - 1) * page_size
    end = start + page_size

    return TruckListResponse(
        trucks=[TruckResponse(**t) for t in trucks[start:end]],
        total=total,
        page=page,
        page_size=page_size,
        has_next=end < total,
    )


@router.post(
    "/trucks/{truck_id}/maintenance",
    response_model=MaintenanceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_maintenance(truck_id: str, request: MaintenanceRequest) -> MaintenanceResponse:
    """Add a maintenance record for a truck."""
    if truck_id not in _trucks_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Truck not found")

    record_id = str(uuid.uuid4())
    record = {
        "id": record_id,
        "truck_id": truck_id,
        **request.model_dump(),
    }
    _maintenance_db[record_id] = record

    return MaintenanceResponse(**record)
