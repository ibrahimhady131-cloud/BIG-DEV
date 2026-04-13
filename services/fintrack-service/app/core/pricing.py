"""Pricing engine for Egyptian logistics — handles quotes, tolls, and fuel calculations."""

from __future__ import annotations

from dataclasses import dataclass

from naql_common.utils import TruckType


@dataclass
class PriceBreakdown:
    """Detailed price breakdown for a shipment quote."""

    fuel_cost_egp: float
    toll_cost_egp: float
    service_fee_egp: float
    insurance_fee_egp: float
    total_egp: float


# Toll rates for major Egyptian routes (simplified "Cartas" calculation)
# Route key: (origin_region, dest_region) → toll in EGP
TOLL_RATES: dict[tuple[str, str], float] = {
    ("EG-CAI", "EG-ALX"): 180.0,  # Cairo → Alexandria (Desert Road)
    ("EG-ALX", "EG-CAI"): 180.0,
    ("EG-CAI", "EG-SUE"): 120.0,  # Cairo → Suez
    ("EG-SUE", "EG-CAI"): 120.0,
    ("EG-CAI", "EG-DLT"): 80.0,  # Cairo → Delta
    ("EG-DLT", "EG-CAI"): 80.0,
    ("EG-CAI", "EG-UEG"): 200.0,  # Cairo → Upper Egypt
    ("EG-UEG", "EG-CAI"): 200.0,
    ("EG-ALX", "EG-DLT"): 60.0,  # Alexandria → Delta
    ("EG-DLT", "EG-ALX"): 60.0,
    ("EG-SUE", "EG-SIN"): 150.0,  # Suez → Sinai
    ("EG-SIN", "EG-SUE"): 150.0,
}

# Fuel rates per km by truck type (EGP/km, based on diesel prices)
FUEL_RATES: dict[TruckType, float] = {
    TruckType.QUARTER_LOAD: 3.0,
    TruckType.HALF_LOAD: 3.5,
    TruckType.FULL_LOAD: 4.5,
    TruckType.JUMBO: 6.0,
    TruckType.TRAILER: 7.5,
    TruckType.REFRIGERATED: 8.0,  # Higher due to cooling unit
    TruckType.TANKER: 7.0,
    TruckType.FLATBED: 6.5,
}

# Service fee percentage
SERVICE_FEE_PCT = 0.08  # 8%
INSURANCE_RATE_PER_KM = 0.5  # EGP per km


def calculate_quote(
    distance_km: float,
    truck_type: TruckType,
    weight_kg: float,
    origin_region: str,
    dest_region: str,
    requires_refrigeration: bool = False,
) -> PriceBreakdown:
    """Calculate a detailed price quote for a shipment.

    Factors:
    - Fuel cost: Based on distance x truck type fuel rate
    - Toll cost: Based on route (origin/dest regions)
    - Service fee: 8% of subtotal
    - Insurance: Based on distance
    - Weight surcharge: Applied for heavy loads
    """
    # Fuel cost
    fuel_rate = FUEL_RATES.get(truck_type, 4.5)
    if requires_refrigeration and truck_type != TruckType.REFRIGERATED:
        fuel_rate *= 1.3  # 30% surcharge for cooling

    fuel_cost = distance_km * fuel_rate

    # Weight surcharge for loads > 10 tons
    if weight_kg > 10000:
        weight_factor = 1.0 + (weight_kg - 10000) / 50000
        fuel_cost *= weight_factor

    # Toll cost
    toll_cost = TOLL_RATES.get((origin_region, dest_region), 50.0)  # Default 50 EGP

    # Insurance
    insurance_fee = distance_km * INSURANCE_RATE_PER_KM

    # Subtotal before service fee
    subtotal = fuel_cost + toll_cost + insurance_fee

    # Service fee
    service_fee = subtotal * SERVICE_FEE_PCT

    # Total
    total = subtotal + service_fee

    return PriceBreakdown(
        fuel_cost_egp=round(fuel_cost, 2),
        toll_cost_egp=round(toll_cost, 2),
        service_fee_egp=round(service_fee, 2),
        insurance_fee_egp=round(insurance_fee, 2),
        total_egp=round(total, 2),
    )
