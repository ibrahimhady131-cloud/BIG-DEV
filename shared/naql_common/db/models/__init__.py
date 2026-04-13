"""ORM models package — re-exports all models for easy import."""

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
from naql_common.db.models.telemetry import (
    DrivingViolation,
    GeofenceEvent,
    TruckPosition,
    TruckTelemetry,
)

__all__ = [
    "ApiKey",
    "DriverPreferences",
    "DrivingViolation",
    "EscrowHold",
    "GeofenceEvent",
    "LedgerAccount",
    "MatchHistory",
    "Notification",
    "Shipment",
    "ShipmentAuditLog",
    "Transaction",
    "Trip",
    "Truck",
    "TruckMaintenance",
    "TruckPosition",
    "TruckTelemetry",
    "User",
    "UserDocument",
]
