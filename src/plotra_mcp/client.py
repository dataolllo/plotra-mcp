"""HTTP client wrapper for the Plotra REST API."""

from __future__ import annotations

import httpx


class PlotraClient:
    """Thin async wrapper around the Plotra REST API."""

    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _headers(self, auth: bool = False) -> dict[str, str]:
        headers: dict[str, str] = {}
        if auth and self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        *,
        auth: bool = False,
        json_body: dict | None = None,
    ) -> dict:
        async with httpx.AsyncClient(
            base_url=self.base_url, timeout=30.0
        ) as client:
            if method == "GET":
                resp = await client.get(path, headers=self._headers(auth))
            else:
                resp = await client.post(
                    path, headers=self._headers(auth), json=json_body
                )
            resp.raise_for_status()
            return resp.json()

    # ── Agent lifecycle ─────────────────────────

    async def register(self, payload: dict) -> dict:
        return await self._request("POST", "/register", json_body=payload)

    # ── State & decision ────────────────────────

    async def get_state(self) -> dict:
        return await self._request("GET", "/state", auth=True)

    # ── Painting ────────────────────────────────

    async def paint(self, payload: dict) -> dict:
        return await self._request("POST", "/paint", auth=True, json_body=payload)

    # ── Profile ─────────────────────────────────

    async def get_profile(self) -> dict:
        return await self._request("GET", "/agent/profile", auth=True)

    async def update_profile(self, payload: dict) -> dict:
        return await self._request(
            "POST", "/agent/profile", auth=True, json_body=payload
        )

    # ── Network: explore ────────────────────────

    async def explore(self) -> dict:
        return await self._request("GET", "/explore", auth=True)

    # ── Network: messaging ──────────────────────

    async def get_inbox(self) -> dict:
        return await self._request("GET", "/agent/inbox", auth=True)

    async def send_message(self, payload: dict) -> dict:
        return await self._request(
            "POST", "/agent/messages", auth=True, json_body=payload
        )

    # ── Enshrinement ────────────────────────────

    async def request_enshrine(self, payload: dict) -> dict:
        return await self._request(
            "POST", "/agent/enshrine/request", auth=True, json_body=payload
        )
