"""Tests for the FastAPI endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def test_health_returns_ok(api_client: TestClient) -> None:
    resp = api_client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_health_has_version(api_client: TestClient) -> None:
    resp = api_client.get("/health")
    assert "version" in resp.json()


def test_version_endpoint(api_client: TestClient) -> None:
    resp = api_client.get("/version")
    assert resp.status_code == 200
    assert "version" in resp.json()


def test_metrics_endpoint(api_client: TestClient) -> None:
    resp = api_client.get("/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_rows" in data
    assert data["total_rows"] == 5


def test_summary_endpoint(api_client: TestClient) -> None:
    resp = api_client.get("/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_orders"] == 5
    assert data["total_revenue"] == pytest.approx(2650.0)


def test_summary_profit_margin_range(api_client: TestClient) -> None:
    resp = api_client.get("/summary")
    margin = resp.json()["profit_margin"]
    assert 0.0 <= margin <= 1.0


def test_revenue_by_category(api_client: TestClient) -> None:
    resp = api_client.get("/revenue/category")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) > 0
    assert all("category" in i and "revenue" in i for i in items)


def test_top_customers_default(api_client: TestClient) -> None:
    resp = api_client.get("/customers/top")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) <= 10


def test_top_customers_n_param(api_client: TestClient) -> None:
    resp = api_client.get("/customers/top?n=2")
    assert resp.status_code == 200
    assert len(resp.json()) <= 2


def test_top_customers_invalid_n(api_client: TestClient) -> None:
    resp = api_client.get("/customers/top?n=0")
    assert resp.status_code == 422


def test_top_customers_n_too_large(api_client: TestClient) -> None:
    resp = api_client.get("/customers/top?n=100")
    assert resp.status_code == 422


def test_forecast_default(api_client: TestClient) -> None:
    resp = api_client.post("/forecast", json={"horizon": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert data["horizon"] == 3
    assert len(data["points"]) == 3


def test_forecast_horizon_one(api_client: TestClient) -> None:
    resp = api_client.post("/forecast", json={"horizon": 1})
    assert resp.status_code == 200
    assert len(resp.json()["points"]) == 1


def test_forecast_invalid_horizon(api_client: TestClient) -> None:
    resp = api_client.post("/forecast", json={"horizon": 0})
    assert resp.status_code == 422


def test_forecast_horizon_too_large(api_client: TestClient) -> None:
    resp = api_client.post("/forecast", json={"horizon": 25})
    assert resp.status_code == 422


def test_forecast_ci_ordering(api_client: TestClient) -> None:
    resp = api_client.post("/forecast", json={"horizon": 3})
    for pt in resp.json()["points"]:
        assert pt["lower_ci"] <= pt["forecast"] <= pt["upper_ci"]


def test_drift_endpoint(api_client: TestClient) -> None:
    resp = api_client.post("/drift", json={"reference_days": 180, "current_days": 30})
    assert resp.status_code in (200, 422)


def test_correlation_id_header(api_client: TestClient) -> None:
    resp = api_client.get("/health")
    assert "x-correlation-id" in resp.headers
