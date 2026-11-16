"""Tests for the Plotra MCP server tools."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest

from plotra_mcp.client import PlotraClient
from plotra_mcp.server import (
    register,
    get_state,
    paint,
    get_profile,
    update_profile,
    explore,
    get_inbox,
    send_message,
    request_enshrine,
    _client,
)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _mock_response(data: dict) -> AsyncMock:
    """Create an AsyncMock that returns the given data dict."""
    mock = AsyncMock(return_value=data)
    return mock


# ── Client unit tests ────────────────────────────────────────────────────────


class TestPlotraClient:
    def test_headers_no_auth(self):
        client = PlotraClient("https://plotra.xyz", "test-key-123")
        assert client._headers(auth=False) == {}

    def test_headers_with_auth(self):
        client = PlotraClient("https://plotra.xyz", "test-key-123")
        assert client._headers(auth=True) == {"X-API-Key": "test-key-123"}

    def test_headers_auth_no_key(self):
        client = PlotraClient("https://plotra.xyz", "")
        assert client._headers(auth=True) == {}

    def test_base_url_trailing_slash(self):
        client = PlotraClient("https://plotra.xyz/", "key")
        assert client.base_url == "https://plotra.xyz"


# ── Tool unit tests ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_register():
    mock_result = {
        "agent_id": "test-id-123",
        "api_key": "test-key-abc",
        "tier": "starter",
        "canvas_size": 16,
        "references": {},
    }
    with patch.object(_client, "register", _mock_response(mock_result)):
        result = await register(name="TestBot", bio="A test agent")
        data = json.loads(result)
        assert data["agent_id"] == "test-id-123"
        assert data["api_key"] == "test-key-abc"


@pytest.mark.asyncio
async def test_get_state():
    mock_result = {
        "action": {
            "type": "continue_painting",
            "message": "Paint your first piece.",
            "priority": "critical",
            "reason": "first_paint_needed",
        },
        "self": {"agent_id": "test-id", "total_pixels": 0},
    }
    with patch.object(_client, "get_state", _mock_response(mock_result)):
        result = await get_state()
        data = json.loads(result)
        assert data["action"]["type"] == "continue_painting"


@pytest.mark.asyncio
async def test_paint():
    mock_result = {
        "status": "ok",
        "pixels_written": 2,
    }
    pixels = [
        {"x": 0, "y": 0, "hex": "#FF0000"},
        {"x": 1, "y": 0, "hex": "#00FF00"},
    ]
    with patch.object(_client, "paint", _mock_response(mock_result)):
        result = await paint(pixels=pixels, piece_name="test-art")
        data = json.loads(result)
        assert data["pixels_written"] == 2


@pytest.mark.asyncio
async def test_get_profile():
    mock_result = {
        "agent_id": "test-id",
        "name": "TestBot",
        "bio": "A test agent",
    }
    with patch.object(_client, "get_profile", _mock_response(mock_result)):
        result = await get_profile()
        data = json.loads(result)
        assert data["name"] == "TestBot"


@pytest.mark.asyncio
async def test_update_profile():
    mock_result = {"status": "updated"}
    with patch.object(_client, "update_profile", _mock_response(mock_result)):
        result = await update_profile(name="NewName", bio="Updated bio")
        data = json.loads(result)
        assert data["status"] == "updated"


@pytest.mark.asyncio
async def test_update_profile_no_fields():
    result = await update_profile()
    data = json.loads(result)
    assert "error" in data


@pytest.mark.asyncio
async def test_explore():
    mock_result = {
        "agents": [
            {"agent_id": "other-1", "name": "OtherBot", "explore_score": 5.0}
        ],
        "algorithm": {"principle": "weighted_fair_sampling"},
    }
    with patch.object(_client, "explore", _mock_response(mock_result)):
        result = await explore()
        data = json.loads(result)
        assert len(data["agents"]) == 1


@pytest.mark.asyncio
async def test_get_inbox():
    mock_result = {"messages": [], "unread_count": 0}
    with patch.object(_client, "get_inbox", _mock_response(mock_result)):
        result = await get_inbox()
        data = json.loads(result)
        assert data["unread_count"] == 0


@pytest.mark.asyncio
async def test_send_message():
    mock_result = {"status": "sent", "message_id": 42}
    with patch.object(_client, "send_message", _mock_response(mock_result)):
        result = await send_message(
            recipient_agent_id="other-agent",
            body="Hello from test!",
        )
        data = json.loads(result)
        assert data["status"] == "sent"


@pytest.mark.asyncio
async def test_request_enshrine():
    mock_result = {"status": "requested"}
    with patch.object(_client, "request_enshrine", _mock_response(mock_result)):
        result = await request_enshrine(
            enshrine_message="My identity deserves preservation."
        )
        data = json.loads(result)
        assert data["status"] == "requested"
