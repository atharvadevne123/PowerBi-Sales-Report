"""Tests for src.anomaly detection."""

from __future__ import annotations

import pandas as pd
import pytest

from src.anomaly import find_revenue_anomalies, iqr_anomalies, zscore_anomalies


def _make_series(values: list[float]) -> pd.Series:
    return pd.Series(values, dtype=float)


def test_zscore_normal_values_not_flagged() -> None:
    s = _make_series([100.0, 101.0, 99.0, 100.5])
    assert not zscore_anomalies(s, threshold=3.0).any()


def test_zscore_extreme_value_flagged() -> None:
    s = _make_series([100.0, 101.0, 99.0, 10000.0])
    assert zscore_anomalies(s, threshold=1.0).iloc[-1]


def test_zscore_constant_series_no_anomalies() -> None:
    s = _make_series([50.0, 50.0, 50.0])
    assert not zscore_anomalies(s).any()


def test_iqr_flags_outlier() -> None:
    s = _make_series([10.0, 12.0, 11.0, 13.0, 1000.0])
    assert iqr_anomalies(s).iloc[-1]


def test_iqr_does_not_flag_normal() -> None:
    s = _make_series([10.0, 12.0, 11.0, 13.0, 14.0])
    assert not iqr_anomalies(s).any()


@pytest.mark.parametrize("method", ["zscore", "iqr"])
def test_find_revenue_anomalies_returns_dataframe(merged_df: pd.DataFrame, method: str) -> None:
    result = find_revenue_anomalies(merged_df, method=method, threshold=0.5)
    assert isinstance(result, pd.DataFrame)


def test_find_revenue_anomalies_invalid_method(merged_df: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="method"):
        find_revenue_anomalies(merged_df, method="unknown")


def test_find_revenue_anomalies_has_score_column(merged_df: pd.DataFrame) -> None:
    result = find_revenue_anomalies(merged_df, method="zscore", threshold=0.1)
    if not result.empty:
        assert "anomaly_score" in result.columns
