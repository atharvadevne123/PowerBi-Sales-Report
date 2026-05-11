"""Tests for app.middleware rate limiting."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware import RateLimitMiddleware, _RATE_LIMIT, _rate_counters


@pytest.fixture()
def limited_app() -> TestClient:
    """TestClient with a fresh app that has rate limiting middleware."""
    _rate_counters.clear()
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware)

    @app.get("/ping")
    async def ping() -> dict:
        return {"ok": True}

    return TestClient(app, raise_server_exceptions=False)


def test_rate_limit_allows_normal_traffic(limited_app: TestClient) -> None:
    resp = limited_app.get("/ping")
    assert resp.status_code == 200


def test_rate_limit_blocks_after_limit(limited_app: TestClient) -> None:
    _rate_counters.clear()
    for _ in range(_RATE_LIMIT):
        limited_app.get("/ping")
    resp = limited_app.get("/ping")
    assert resp.status_code == 429


def test_rate_limit_response_body(limited_app: TestClient) -> None:
    _rate_counters.clear()
    for _ in range(_RATE_LIMIT):
        limited_app.get("/ping")
    resp = limited_app.get("/ping")
    assert "Rate limit" in resp.json().get("detail", "")
