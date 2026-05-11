"""Tests for src.monitoring drift detection."""

from __future__ import annotations

import pandas as pd
import pytest

from src.monitoring import detect_drift, prediction_log_summary


def _make_df(amounts: list[float], profits: list[float], quantities: list[int]) -> pd.DataFrame:
    return pd.DataFrame({"Amount": amounts, "Profit": profits, "Quantity": quantities})


def test_detect_drift_no_drift() -> None:
    ref = _make_df([100, 200, 300, 400, 500], [10, 20, 30, 40, 50], [1, 2, 3, 4, 5])
    cur = _make_df([110, 210, 310, 410, 510], [11, 21, 31, 41, 51], [1, 2, 3, 4, 5])
    result = detect_drift(ref, cur)
    assert "drift_detected" in result
    assert isinstance(result["drift_detected"], bool)


def test_detect_drift_obvious_drift() -> None:
    import numpy as np

    rng = np.random.default_rng(42)
    ref = _make_df(rng.normal(100, 5, 100).tolist(), rng.normal(20, 2, 100).tolist(), [1] * 100)
    cur = _make_df(rng.normal(9000, 5, 100).tolist(), rng.normal(1800, 2, 100).tolist(), [1] * 100)
    result = detect_drift(ref, cur, alpha=0.05)
    assert result["drift_detected"] is True


def test_detect_drift_returns_per_column_results() -> None:
    ref = _make_df([100, 200], [10, 20], [1, 2])
    cur = _make_df([100, 200], [10, 20], [1, 2])
    result = detect_drift(ref, cur)
    assert "Amount" in result["columns"]
    assert "Profit" in result["columns"]
    assert "Quantity" in result["columns"]


def test_detect_drift_missing_column_skipped() -> None:
    ref = pd.DataFrame({"Amount": [100, 200], "Profit": [10, 20]})
    cur = pd.DataFrame({"Amount": [100, 200], "Profit": [10, 20]})
    result = detect_drift(ref, cur)
    assert "Quantity" not in result["columns"]


def test_prediction_log_summary_empty() -> None:
    result = prediction_log_summary([])
    assert result["count"] == 0
    assert result["mean_forecast"] is None


def test_prediction_log_summary_values() -> None:
    logs = [{"forecast": 100.0, "period": "2023-01"}, {"forecast": 200.0, "period": "2023-02"}]
    result = prediction_log_summary(logs)
    assert result["count"] == 2
    assert result["mean_forecast"] == pytest.approx(150.0)
    assert result["min_forecast"] == pytest.approx(100.0)
    assert result["max_forecast"] == pytest.approx(200.0)
