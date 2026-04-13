"""Pricing engine for Egyptian logistics - handles quotes, tolls, and fuel calculations.

Egyptian "Cartas" (road tolls) are calculated per-route based on the major
highway corridors. Rates reflect 2024/2025 toll gate pricing for heavy vehicles
on expressways managed by the Egyptian National Roads Authority.
"""

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


# ── Egyptian Toll Gates ("Cartas") ─────────────────────────────────────
#
# Toll rates for major Egyptian highway corridors.
# Key: (origin_region, dest_region) → total tolls in EGP for heavy trucks.
#
# Major corridors covered:
#   - Cairo-Alexandria Desert Road  (طريق الصحراوي)
#   - Cairo-Ain Sokhna Road         (طريق العين السخنة)
#   - Cairo Ring Road               (الطريق الدائري)
#   - Rod El Farag Axis             (محور روض الفرج)
#   - Cairo-Ismailia Road           (طريق الإسماعيلية)
#   - Cairo-Suez Road               (طريق السويس)
#   - Regional Ring Road            (الطريق الإقليمي)
#   - Upper Egypt Highway           (طريق الصعيد)

TOLL_RATES: dict[tuple[str, str], float] = {
    # Cairo ↔ Alexandria (Desert Road - 3 toll gates)
    ("EG-CAI", "EG-ALX"): 180.0,
    ("EG-ALX", "EG-CAI"): 180.0,
    # Cairo ↔ Suez (Cairo-Suez Road - 2 toll gates)
    ("EG-CAI", "EG-SUE"): 120.0,
    ("EG-SUE", "EG-CAI"): 120.0,
    # Cairo ↔ Delta (Agricultural Road - 1 toll gate)
    ("EG-CAI", "EG-DLT"): 80.0,
    ("EG-DLT", "EG-CAI"): 80.0,
    # Cairo ↔ Upper Egypt (Upper Egypt Highway - multiple toll gates)
    ("EG-CAI", "EG-UEG"): 200.0,
    ("EG-UEG", "EG-CAI"): 200.0,
    # Alexandria ↔ Delta (International Coastal Road)
    ("EG-ALX", "EG-DLT"): 60.0,
    ("EG-DLT", "EG-ALX"): 60.0,
    # Suez ↔ Sinai (Ahmed Hamdi Tunnel)
    ("EG-SUE", "EG-SIN"): 150.0,
    ("EG-SIN", "EG-SUE"): 150.0,
    # ── Sokhna corridor (critical for container traffic) ──
    # Sokhna Port ↔ Cairo (via Ain Sokhna Road - 2 toll gates + Ring Road)
    ("EG-SOK", "EG-CAI"): 140.0,
    ("EG-CAI", "EG-SOK"): 140.0,
    # Sokhna Port ↔ 6th October (via Regional Ring Road - 3 toll gates)
    ("EG-SOK", "EG-OCT"): 120.0,
    ("EG-OCT", "EG-SOK"): 120.0,
    # Sokhna Port ↔ 10th Ramadan (via Suez Road - 2 toll gates)
    ("EG-SOK", "EG-RAM"): 100.0,
    ("EG-RAM", "EG-SOK"): 100.0,
    # ── Rod El Farag Axis & Ring Road corridors ──
    # Cairo ↔ 6th October (via Rod El Farag Axis / Mehwar - 1 toll gate)
    ("EG-CAI", "EG-OCT"): 60.0,
    ("EG-OCT", "EG-CAI"): 60.0,
    # Cairo ↔ 10th Ramadan (via Cairo-Ismailia Road - 1 toll gate)
    ("EG-CAI", "EG-RAM"): 75.0,
    ("EG-RAM", "EG-CAI"): 75.0,
    # ── Industrial zone corridors ──
    # 6th October ↔ Alexandria (via Desert Road - 2 toll gates)
    ("EG-OCT", "EG-ALX"): 150.0,
    ("EG-ALX", "EG-OCT"): 150.0,
    # 10th Ramadan ↔ Suez (via Ismailia Road - 1 toll gate)
    ("EG-RAM", "EG-SUE"): 90.0,
    ("EG-SUE", "EG-RAM"): 90.0,
    # ── Port corridors ──
    # Damietta ↔ Cairo (via International Coastal → Delta Road)
    ("EG-DAM", "EG-CAI"): 160.0,
    ("EG-CAI", "EG-DAM"): 160.0,
    # Port Said ↔ Cairo (via Ismailia Road)
    ("EG-PSD", "EG-CAI"): 170.0,
    ("EG-CAI", "EG-PSD"): 170.0,
    # Damietta ↔ 10th Ramadan
    ("EG-DAM", "EG-RAM"): 130.0,
    ("EG-RAM", "EG-DAM"): 130.0,
    # ── Cross-regional ──
    # 6th October ↔ Upper Egypt (via Fayoum Road)
    ("EG-OCT", "EG-UEG"): 180.0,
    ("EG-UEG", "EG-OCT"): 180.0,
    # Suez ↔ Ismailia
    ("EG-SUE", "EG-ISM"): 70.0,
    ("EG-ISM", "EG-SUE"): 70.0,
    # Alexandria ↔ Damietta (via International Coastal Road)
    ("EG-ALX", "EG-DAM"): 120.0,
    ("EG-DAM", "EG-ALX"): 120.0,
}

# ── Heavy vehicle surcharge multipliers ────────────────────────────────
# Egyptian toll gates charge more for heavier vehicles.
TOLL_TRUCK_MULTIPLIERS: dict[TruckType, float] = {
    TruckType.QUARTER_LOAD: 0.5,
    TruckType.HALF_LOAD: 0.7,
    TruckType.FULL_LOAD: 1.0,
    TruckType.JUMBO: 1.3,
    TruckType.TRAILER: 1.5,
    TruckType.REFRIGERATED: 1.2,
    TruckType.TANKER: 1.4,
    TruckType.FLATBED: 1.3,
}

# Fuel rates per km by truck type (EGP/km, based on 2025 diesel prices ~10.25 EGP/L)
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
    - Toll cost: Based on route (origin/dest regions) with truck-type multiplier
    - Service fee: 8% of subtotal
    - Insurance: Based on distance
    - Weight surcharge: Applied for heavy loads > 10 tons
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

    # Toll cost - base rate from route table, adjusted by truck type multiplier
    base_toll = TOLL_RATES.get((origin_region, dest_region), 50.0)
    truck_multiplier = TOLL_TRUCK_MULTIPLIERS.get(truck_type, 1.0)
    toll_cost = base_toll * truck_multiplier

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
