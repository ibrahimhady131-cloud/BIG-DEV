"""GraphQL API Gateway for Naql.ai — Strawberry-based schema."""

from __future__ import annotations

from datetime import datetime

import strawberry

# ── Types ──────────────────────────────────────────────────


@strawberry.type
class User:
    """User account type."""

    id: str
    email: str
    phone: str
    full_name: str
    role: str
    kyc_status: str
    reputation_score: float
    region_code: str
    is_active: bool
    created_at: datetime


@strawberry.type
class AuthPayload:
    """Authentication response type."""

    user_id: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: str
    region_code: str


@strawberry.type
class Truck:
    """Truck entity type."""

    id: str
    owner_id: str
    license_plate: str
    truck_type: str
    load_capacity_kg: int
    status: str
    region_code: str
    has_refrigeration: bool
    vin: str | None = None
    make: str | None = None
    model: str | None = None


@strawberry.type
class MatchCandidate:
    """A matched driver/truck candidate."""

    driver_id: str
    truck_id: str
    truck_type: str
    score: float
    distance_km: float
    eta_minutes: int
    driver_rating: float


@strawberry.type
class MatchResult:
    """Match result from the matching engine."""

    match_id: str
    candidates: list[MatchCandidate]
    total_searched: int


@strawberry.type
class PriceQuote:
    """Price quote for a shipment."""

    quote_id: str
    total_egp: float
    fuel_cost_egp: float
    toll_cost_egp: float
    service_fee_egp: float
    insurance_fee_egp: float
    valid_until: datetime


@strawberry.type
class Balance:
    """User account balance."""

    user_id: str
    available_egp: float
    held_egp: float
    total_egp: float


@strawberry.type
class ChatResponse:
    """AI agent chat response."""

    session_id: str
    response: str
    intent: str


@strawberry.type
class Shipment:
    """Shipment entity type."""

    id: str
    reference_number: str
    status: str
    origin_address: str
    dest_address: str
    commodity_type: str
    weight_kg: float
    quoted_price_egp: float | None = None


@strawberry.type
class TelemetryStats:
    """Real-time telemetry processing statistics."""

    position_buffer_size: int
    telemetry_buffer_size: int


# ── Inputs ─────────────────────────────────────────────────


@strawberry.input
class RegisterInput:
    """Input for user registration."""

    email: str
    phone: str
    password: str
    full_name: str
    role: str = "client_individual"
    region_code: str = "EG-CAI"
    national_id: str | None = None


@strawberry.input
class LoginInput:
    """Input for user login."""

    email: str
    password: str


@strawberry.input
class CoordinateInput:
    """Geographic coordinate input."""

    latitude: float
    longitude: float


@strawberry.input
class MatchRequestInput:
    """Input for requesting a match."""

    shipment_id: str
    origin: CoordinateInput
    destination: CoordinateInput
    required_truck_type: str | None = None
    weight_kg: float = 0.0
    requires_refrigeration: bool = False
    search_radius_km: float = 20.0


@strawberry.input
class QuoteInput:
    """Input for getting a price quote."""

    distance_km: float
    truck_type: str
    weight_kg: float
    origin_region: str
    dest_region: str
    requires_refrigeration: bool = False


@strawberry.input
class ChatInput:
    """Input for AI agent chat."""

    user_id: str
    message: str
    session_id: str | None = None
    language: str = "en"


# ── Queries ────────────────────────────────────────────────


@strawberry.type
class Query:
    """Root GraphQL queries."""

    @strawberry.field
    async def me(self, info: strawberry.types.Info) -> User | None:
        """Get current authenticated user."""
        # Would call Identity Service via gRPC/HTTP
        return None

    @strawberry.field
    async def user(self, user_id: str) -> User | None:
        """Get a user by ID."""
        return None

    @strawberry.field
    async def truck(self, truck_id: str) -> Truck | None:
        """Get a truck by ID."""
        return None

    @strawberry.field
    async def trucks(
        self,
        page: int = 1,
        page_size: int = 20,
        truck_type: str | None = None,
        region_code: str | None = None,
    ) -> list[Truck]:
        """List trucks with filtering."""
        return []

    @strawberry.field
    async def shipment(self, shipment_id: str) -> Shipment | None:
        """Get a shipment by ID."""
        return None

    @strawberry.field
    async def balance(self, user_id: str) -> Balance | None:
        """Get user account balance."""
        return None

    @strawberry.field
    async def telemetry_stats(self) -> TelemetryStats:
        """Get real-time telemetry processing stats."""
        return TelemetryStats(position_buffer_size=0, telemetry_buffer_size=0)


# ── Mutations ──────────────────────────────────────────────


@strawberry.type
class Mutation:
    """Root GraphQL mutations."""

    @strawberry.mutation
    async def register(self, input: RegisterInput) -> AuthPayload:
        """Register a new user."""
        # Would call Identity Service
        return AuthPayload(
            user_id="placeholder",
            access_token="placeholder",
            refresh_token="placeholder",
            role=input.role,
            region_code=input.region_code,
        )

    @strawberry.mutation
    async def login(self, input: LoginInput) -> AuthPayload:
        """Login and get authentication tokens."""
        return AuthPayload(
            user_id="placeholder",
            access_token="placeholder",
            refresh_token="placeholder",
            role="client_individual",
            region_code="EG-CAI",
        )

    @strawberry.mutation
    async def request_match(self, input: MatchRequestInput) -> MatchResult:
        """Request a truck/driver match for a shipment."""
        return MatchResult(match_id="placeholder", candidates=[], total_searched=0)

    @strawberry.mutation
    async def get_quote(self, input: QuoteInput) -> PriceQuote:
        """Get a price quote for a shipment."""
        return PriceQuote(
            quote_id="placeholder",
            total_egp=0.0,
            fuel_cost_egp=0.0,
            toll_cost_egp=0.0,
            service_fee_egp=0.0,
            insurance_fee_egp=0.0,
            valid_until=datetime.now(),
        )

    @strawberry.mutation
    async def chat(self, input: ChatInput) -> ChatResponse:
        """Send a message to the Naql.ai AI agent."""
        return ChatResponse(
            session_id="placeholder",
            response="placeholder",
            intent="general",
        )


# ── Schema ─────────────────────────────────────────────────

schema = strawberry.Schema(query=Query, mutation=Mutation)
