"""Matching Engine API routes."""

from __future__ import annotations

from fastapi import APIRouter

from naql_common.geo import Coordinate

from ..engine.matcher import GeoMatcher, MatchRequest, TruckCandidate
from ..schemas.matching import (
    AvailableTrucksRequestSchema,
    MatchCandidateSchema,
    MatchDecisionSchema,
    MatchRequestSchema,
    MatchResponseSchema,
    TruckLocationUpdateSchema,
)

router = APIRouter(prefix="/api/v1", tags=["matching"])

# Global matcher instance
geo_matcher = GeoMatcher()

# Track match decisions
_match_decisions: dict[str, dict] = {}


@router.post("/match", response_model=MatchResponseSchema)
async def request_match(request: MatchRequestSchema) -> MatchResponseSchema:
    """Find optimal truck/driver matches for a shipment."""
    match_req = MatchRequest(
        shipment_id=request.shipment_id,
        origin=Coordinate(request.origin.latitude, request.origin.longitude),
        destination=Coordinate(request.destination.latitude, request.destination.longitude),
        required_truck_type=request.required_truck_type,
        weight_kg=request.weight_kg,
        requires_refrigeration=request.requires_refrigeration,
        search_radius_km=request.search_radius_km,
        max_candidates=request.max_candidates,
    )

    result = geo_matcher.match(match_req)

    return MatchResponseSchema(
        match_id=result.match_id,
        candidates=[
            MatchCandidateSchema(
                driver_id=c.driver_id,
                truck_id=c.truck_id,
                truck_type=c.truck_type,
                score=c.score,
                distance_km=c.distance_km,
                eta_minutes=c.eta_minutes,
                driver_rating=c.driver_rating,
            )
            for c in result.candidates
        ],
        total_searched=result.total_searched,
    )


@router.post("/match/available-trucks")
async def get_available_trucks(request: AvailableTrucksRequestSchema) -> dict:
    """Query available trucks in a geographic area."""
    origin = Coordinate(request.center.latitude, request.center.longitude)

    candidates = geo_matcher.find_nearby_trucks(
        origin=origin,
        radius_km=request.radius_km,
        truck_type=request.truck_type,
        min_capacity_kg=request.min_capacity_kg,
    )

    return {
        "trucks": [
            {
                "driver_id": c.driver_id,
                "truck_id": c.truck_id,
                "truck_type": c.truck_type,
                "distance_km": c.distance_km,
                "eta_minutes": c.eta_minutes,
                "driver_rating": c.driver_rating,
            }
            for c in candidates
        ],
        "total": len(candidates),
    }


@router.post("/match/decision")
async def respond_to_match(request: MatchDecisionSchema) -> dict:
    """Record a driver's response to a match offer."""
    _match_decisions[request.match_id] = {
        "driver_id": request.driver_id,
        "decision": request.decision,
    }

    return {
        "success": True,
        "message": f"Match {request.decision} by driver {request.driver_id}",
    }


@router.post("/trucks/location")
async def update_truck_location(request: TruckLocationUpdateSchema) -> dict:
    """Update a truck's real-time position in the geo-index."""
    candidate = TruckCandidate(
        driver_id=request.driver_id,
        truck_id=request.truck_id,
        truck_type="unknown",  # Would be fetched from fleet service
        load_capacity_kg=0,
        has_refrigeration=False,
        latitude=request.latitude,
        longitude=request.longitude,
        driver_rating=4.5,  # Would be fetched from identity service
    )

    geo_matcher.register_truck_position(candidate)
    coord = Coordinate(request.latitude, request.longitude)

    return {
        "received": True,
        "h3_index": coord.to_h3(),
    }
