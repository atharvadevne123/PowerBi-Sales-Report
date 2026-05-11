"""Tests for src.forecasting."""

from __future__ import annotations

import pandas as pd
import pytest

from src.forecasting import detect_seasonality, forecast_revenue


def test_forecast_returns_correct_horizon(merged_df: pd.DataFrame) -> None:
    result = forecast_revenue(merged_df, horizon=3)
    assert len(result) == 3


def test_forecast_columns_present(merged_df: pd.DataFrame) -> None:
    result = forecast_revenue(merged_df, horizon=2)
    assert set(result.columns) == {"period", "forecast", "lower_ci", "upper_ci"}


def test_forecast_ci_ordering(merged_df: pd.DataFrame) -> None:
    result = forecast_revenue(merged_df, horizon=3)
    for _, row in result.iterrows():
        assert row["lower_ci"] <= row["forecast"] <= row["upper_ci"]


@pytest.mark.parametrize("horizon", [1, 6, 12])
def test_forecast_various_horizons(merged_df: pd.DataFrame, horizon: int) -> None:
    result = forecast_revenue(merged_df, horizon=horizon)
    assert len(result) == horizon


def test_forecast_invalid_horizon(merged_df: pd.DataFrame) -> None:
    with pytest.raises(ValueError):
        forecast_revenue(merged_df, horizon=0)


def test_forecast_too_little_data() -> None:
    df = pd.DataFrame({
        "Order Date": pd.to_datetime(["2023-01-15"]),
        "Amount": [1000.0],
    })
    with pytest.raises(ValueError, match="at least 2 months"):
        forecast_revenue(df, horizon=1)


def test_detect_seasonality_keys(merged_df: pd.DataFrame) -> None:
    result = detect_seasonality(merged_df)
    assert isinstance(result, dict)
    assert all(isinstance(k, str) for k in result)


def test_detect_seasonality_values_positive(merged_df: pd.DataFrame) -> None:
    result = detect_seasonality(merged_df)
    for v in result.values():
        assert v >= 0
