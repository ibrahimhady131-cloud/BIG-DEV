"""Pydantic schemas for Matching Engine API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CoordinateSchema(BaseModel):
    """Geographic coordinate."""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class MatchRequestSchema(BaseModel):
    """Request schema for finding matches."""

    shipment_id: str
    origin: CoordinateSchema
    destination: CoordinateSchema
    required_truck_type: str | None = None
    weight_kg: float = Field(0.0, ge=0)
    requires_refrigeration: bool = False
    search_radius_km: float = Field(20.0, gt=0, le=100)
    max_candidates: int = Field(10, gt=0, le=50)


class MatchCandidateSchema(BaseModel):
    """A matched truck/driver candidate."""

    driver_id: str
    truck_id: str
    truck_type: str
    score: float
    distance_km: float
    eta_minutes: int
    driver_rating: float


class MatchResponseSchema(BaseModel):
    """Response schema for match results."""

    match_id: str
    candidates: list[MatchCandidateSchema]
    total_searched: int


class AvailableTrucksRequestSchema(BaseModel):
    """Request schema for querying available trucks."""

    center: CoordinateSchema
    radius_km: float = Field(20.0, gt=0, le=100)
    truck_type: str | None = None
    min_capacity_kg: int = Field(0, ge=0)


class TruckLocationUpdateSchema(BaseModel):
    """Schema for updating a truck's real-time location."""

    truck_id: str
    driver_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    speed_kmh: float = Field(0.0, ge=0)
    heading: float = Field(0.0, ge=0, le=360)


class MatchDecisionSchema(BaseModel):
    """Schema for driver's match decision."""

    match_id: str
    driver_id: str
    decision: str = Field(..., pattern=r"^(accepted|rejected)$")
