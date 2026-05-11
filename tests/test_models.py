"""Tests for app.models Pydantic validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models import DriftRequest, ForecastRequest, MetricsResponse, SummaryResponse


def test_forecast_request_default_horizon() -> None:
    req = ForecastRequest()
    assert req.horizon == 3


def test_forecast_request_valid_horizon() -> None:
    req = ForecastRequest(horizon=12)
    assert req.horizon == 12


def test_forecast_request_rejects_zero() -> None:
    with pytest.raises(ValidationError):
        ForecastRequest(horizon=0)


def test_forecast_request_rejects_negative() -> None:
    with pytest.raises(ValidationError):
        ForecastRequest(horizon=-1)


def test_forecast_request_rejects_too_large() -> None:
    with pytest.raises(ValidationError):
        ForecastRequest(horizon=25)


@pytest.mark.parametrize("horizon", [1, 3, 12, 24])
def test_forecast_request_valid_range(horizon: int) -> None:
    req = ForecastRequest(horizon=horizon)
    assert req.horizon == horizon


def test_drift_request_defaults() -> None:
    req = DriftRequest()
    assert req.reference_days == 180
    assert req.current_days == 30


def test_drift_request_invalid_reference_days() -> None:
    with pytest.raises(ValidationError):
        DriftRequest(reference_days=1)


def test_summary_response_fields() -> None:
    resp = SummaryResponse(
        total_orders=10,
        total_revenue=5000.0,
        total_profit=1000.0,
        total_quantity=50,
        profit_margin=0.2,
        avg_order_value=500.0,
    )
    assert resp.total_orders == 10
    assert resp.profit_margin == pytest.approx(0.2)


def test_metrics_response_optional_dates() -> None:
    resp = MetricsResponse(total_rows=100, date_range_start=None, date_range_end=None)
    assert resp.date_range_start is None
