"""HTTP client for internal service communication from the GraphQL Gateway."""

from __future__ import annotations

import os
from typing import Any

import httpx


class ServiceClient:
    """Async HTTP client that proxies GraphQL requests to internal microservices."""

    def __init__(self) -> None:
        self._identity_url = os.getenv("GATEWAY_IDENTITY_SERVICE_URL", "http://localhost:8001")
        self._fleet_url = os.getenv("GATEWAY_FLEET_SERVICE_URL", "http://localhost:8002")
        self._matching_url = os.getenv("GATEWAY_MATCHING_SERVICE_URL", "http://localhost:8003")
        self._fintrack_url = os.getenv("GATEWAY_FINTRACK_SERVICE_URL", "http://localhost:8004")
        self._agent_url = os.getenv("GATEWAY_AGENT_SERVICE_URL", "http://localhost:8005")
        self._client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        await self._client.aclose()

    # ── Identity Service ───────────────────────────────────────

    async def register(self, data: dict[str, Any]) -> dict[str, Any]:
        """POST /api/v1/auth/register → Identity Service."""
        resp = await self._client.post(f"{self._identity_url}/api/v1/auth/register", json=data)
        resp.raise_for_status()
        return resp.json()

    async def login(self, email: str, password: str) -> dict[str, Any]:
        """POST /api/v1/auth/login → Identity Service."""
        resp = await self._client.post(
            f"{self._identity_url}/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        resp.raise_for_status()
        return resp.json()

    async def get_user(self, user_id: str) -> dict[str, Any] | None:
        """GET /api/v1/users/{user_id} → Identity Service."""
        resp = await self._client.get(f"{self._identity_url}/api/v1/users/{user_id}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def get_me(self, token: str) -> dict[str, Any] | None:
        """GET /api/v1/users/me → Identity Service (authenticated)."""
        resp = await self._client.get(
            f"{self._identity_url}/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        if resp.status_code == 401:
            return None
        resp.raise_for_status()
        return resp.json()

    # ── Fleet Service ──────────────────────────────────────────

    async def get_truck(self, truck_id: str) -> dict[str, Any] | None:
        """GET /api/v1/trucks/{truck_id} → Fleet Service."""
        resp = await self._client.get(f"{self._fleet_url}/api/v1/trucks/{truck_id}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def list_trucks(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        truck_type: str | None = None,
        region_code: str | None = None,
    ) -> list[dict[str, Any]]:
        """GET /api/v1/trucks → Fleet Service."""
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if truck_type:
            params["truck_type"] = truck_type
        if region_code:
            params["region_code"] = region_code
        resp = await self._client.get(f"{self._fleet_url}/api/v1/trucks", params=params)
        resp.raise_for_status()
        data = resp.json()
        return data.get("trucks", [])

    # ── Matching Engine ────────────────────────────────────────

    async def request_match(self, data: dict[str, Any]) -> dict[str, Any]:
        """POST /api/v1/match → Matching Engine."""
        resp = await self._client.post(f"{self._matching_url}/api/v1/match", json=data)
        resp.raise_for_status()
        return resp.json()

    # ── FinTrack Service ───────────────────────────────────────

    async def get_balance(self, user_id: str) -> dict[str, Any] | None:
        """GET /api/v1/wallets/{user_id}/balance → FinTrack Service."""
        resp = await self._client.get(
            f"{self._fintrack_url}/api/v1/wallets/{user_id}/balance"
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def get_quote(self, data: dict[str, Any]) -> dict[str, Any]:
        """POST /api/v1/pricing/quote → FinTrack Service."""
        resp = await self._client.post(
            f"{self._fintrack_url}/api/v1/pricing/quote", json=data
        )
        resp.raise_for_status()
        return resp.json()

    # ── Agent Orchestrator ─────────────────────────────────────

    async def chat(self, data: dict[str, Any]) -> dict[str, Any]:
        """POST /api/v1/agent/chat → Agent Orchestrator."""
        resp = await self._client.post(f"{self._agent_url}/api/v1/agent/chat", json=data)
        resp.raise_for_status()
        return resp.json()
