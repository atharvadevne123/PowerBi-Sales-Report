"""Data drift detection using the Kolmogorov-Smirnov test."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)

_NUMERIC_COLS = ["Amount", "Profit", "Quantity"]


def detect_drift(
    reference: pd.DataFrame,
    current: pd.DataFrame,
    alpha: float = 0.05,
) -> dict[str, Any]:
    """Run KS test on numeric columns to detect distribution drift.

    Args:
        reference: Baseline dataset (e.g. historical month).
        current: Incoming dataset to compare against the baseline.
        alpha: Significance level for the KS test.

    Returns:
        Dict with per-column results and an overall 'drift_detected' flag.
    """
    results: dict[str, Any] = {"alpha": alpha, "columns": {}, "drift_detected": False}

    for col in _NUMERIC_COLS:
        if col not in reference.columns or col not in current.columns:
            logger.warning("Column %s missing from one of the DataFrames; skipping", col)
            continue

        ref_vals = reference[col].dropna().values
        cur_vals = current[col].dropna().values

        if len(ref_vals) == 0 or len(cur_vals) == 0:
            logger.warning("Empty data for column %s; skipping", col)
            continue

        stat, p_value = stats.ks_2samp(ref_vals, cur_vals)
        drifted = bool(p_value < alpha)
        results["columns"][col] = {
            "ks_statistic": round(float(stat), 6),
            "p_value": round(float(p_value), 6),
            "drift_detected": drifted,
        }
        if drifted:
            results["drift_detected"] = True
            logger.warning("Drift detected in column '%s' (p=%.4f)", col, p_value)

    return results


def prediction_log_summary(logs: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarise a list of prediction log entries.

    Args:
        logs: Each entry should contain at least 'forecast' and 'period'.

    Returns:
        Dict with count, mean_forecast, min_forecast, max_forecast.
    """
    if not logs:
        return {"count": 0, "mean_forecast": None, "min_forecast": None, "max_forecast": None}

    forecasts = [e["forecast"] for e in logs if "forecast" in e]
    arr = np.array(forecasts, dtype=float)
    return {
        "count": len(forecasts),
        "mean_forecast": round(float(arr.mean()), 2),
        "min_forecast": round(float(arr.min()), 2),
        "max_forecast": round(float(arr.max()), 2),
    }
