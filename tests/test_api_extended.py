"""Extended API tests for aggregation endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_clv_endpoint_returns_list(api_client: TestClient) -> None:
    resp = api_client.get("/customers/clv")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_clv_endpoint_has_required_fields(api_client: TestClient) -> None:
    resp = api_client.get("/customers/clv")
    items = resp.json()
    if items:
        assert "clv" in items[0]
        assert "orders" in items[0]


def test_quarterly_revenue_endpoint(api_client: TestClient) -> None:
    resp = api_client.get("/revenue/quarterly")
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)
    if items:
        assert "quarter" in items[0]
        assert "revenue" in items[0]


def test_quarterly_revenue_positive_values(api_client: TestClient) -> None:
    resp = api_client.get("/revenue/quarterly")
    for item in resp.json():
        assert item["revenue"] >= 0


def test_subcategory_profitability_endpoint(api_client: TestClient) -> None:
    resp = api_client.get("/subcategories/profitability")
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list)


def test_subcategory_profitability_has_margin(api_client: TestClient) -> None:
    resp = api_client.get("/subcategories/profitability")
    items = resp.json()
    if items:
        assert "margin" in items[0]


def test_revenue_category_sorted_descending(api_client: TestClient) -> None:
    resp = api_client.get("/revenue/category")
    items = resp.json()
    revenues = [i["revenue"] for i in items]
    assert revenues == sorted(revenues, reverse=True)


def test_summary_avg_order_value_positive(api_client: TestClient) -> None:
    resp = api_client.get("/summary")
    assert resp.json()["avg_order_value"] > 0
