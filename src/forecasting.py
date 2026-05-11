"""Time-series revenue forecasting using linear trend + seasonal decomposition."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

logger = logging.getLogger(__name__)


def _series_to_monthly(df: pd.DataFrame) -> pd.Series:
    """Aggregate merged DataFrame to monthly revenue series."""
    df = df.copy()
    df["Month"] = df["Order Date"].dt.to_period("M")
    return df.groupby("Month")["Amount"].sum().sort_index()


def forecast_revenue(
    df: pd.DataFrame,
    horizon: int = 3,
) -> pd.DataFrame:
    """Forecast monthly revenue using ordinary least-squares trend.

    Args:
        df: Merged sales DataFrame with 'Order Date' and 'Amount'.
        horizon: Number of months ahead to forecast.

    Returns:
        DataFrame with columns ['period', 'forecast', 'lower_ci', 'upper_ci'].

    Raises:
        ValueError: If df has fewer than 2 months of data.
    """
    if horizon <= 0:
        raise ValueError("horizon must be a positive integer")

    monthly = _series_to_monthly(df)
    if len(monthly) < 2:
        raise ValueError("Need at least 2 months of data to forecast")

    X = np.arange(len(monthly)).reshape(-1, 1)
    y = monthly.values.astype(float)

    model = LinearRegression()
    model.fit(X, y)

    residuals = y - model.predict(X)
    std_err = float(np.std(residuals, ddof=1))

    last_period = monthly.index[-1]
    future_periods = [last_period + i for i in range(1, horizon + 1)]
    X_future = np.arange(len(monthly), len(monthly) + horizon).reshape(-1, 1)
    preds = model.predict(X_future)

    rows = []
    for period, pred in zip(future_periods, preds):
        rows.append(
            {
                "period": str(period),
                "forecast": round(float(pred), 2),
                "lower_ci": round(float(pred - 1.96 * std_err), 2),
                "upper_ci": round(float(pred + 1.96 * std_err), 2),
            }
        )
    logger.info("Forecasted %d month(s) ahead", horizon)
    return pd.DataFrame(rows)


def detect_seasonality(df: pd.DataFrame) -> dict[str, float]:
    """Return average revenue per calendar month (1-12) to expose seasonality.

    Args:
        df: Merged sales DataFrame.

    Returns:
        Dict mapping month number (as string) to average monthly revenue.
    """
    df = df.copy()
    df["CalMonth"] = df["Order Date"].dt.month
    avg = df.groupby("CalMonth")["Amount"].mean()
    return {str(k): round(float(v), 2) for k, v in avg.items()}
