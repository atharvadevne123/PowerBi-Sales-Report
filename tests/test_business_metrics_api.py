"""Tests for business metrics API endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_growth_rate_endpoint(api_client: TestClient) -> None:
    resp = api_client.get("/business-metrics/growth-rate")
    assert resp.status_code == 200
    assert "growth_rate" in resp.json()


def test_retention_endpoint_default(api_client: TestClient) -> None:
    resp = api_client.get("/business-metrics/retention")
    assert resp.status_code == 200
    data = resp.json()
    assert "retention_rate" in data
    assert 0.0 <= data["retention_rate"] <= 1.0


def test_retention_endpoint_custom_window(api_client: TestClient) -> None:
    resp = api_client.get("/business-metrics/retention?window_days=365")
    assert resp.status_code == 200
    assert resp.json()["window_days"] == 365


def test_retention_invalid_window(api_client: TestClient) -> None:
    resp = api_client.get("/business-metrics/retention?window_days=0")
    assert resp.status_code == 422


def test_gini_endpoint_amount(api_client: TestClient) -> None:
    resp = api_client.get("/business-metrics/gini?column=Amount")
    assert resp.status_code == 200
    assert 0.0 <= resp.json()["gini"] <= 1.0


def test_gini_endpoint_invalid_column(api_client: TestClient) -> None:
    resp = api_client.get("/business-metrics/gini?column=InvalidCol")
    assert resp.status_code == 422


def test_basket_size_endpoint(api_client: TestClient) -> None:
    resp = api_client.get("/business-metrics/basket-size")
    assert resp.status_code == 200
    assert resp.json()["avg_basket_size"] > 0
