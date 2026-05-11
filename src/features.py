"""Feature engineering transformations for ML models over the sales dataset."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add calendar-based features derived from 'Order Date'.

    Args:
        df: Merged sales DataFrame with a parsed 'Order Date' column.

    Returns:
        DataFrame with new columns: year, month, quarter, day_of_week,
        is_weekend, week_of_year.
    """
    df = df.copy()
    df["year"] = df["Order Date"].dt.year
    df["month"] = df["Order Date"].dt.month
    df["quarter"] = df["Order Date"].dt.quarter
    df["day_of_week"] = df["Order Date"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)
    df["week_of_year"] = df["Order Date"].dt.isocalendar().week.astype(int)
    logger.debug("Added time features; shape=%s", df.shape)
    return df


def add_rolling_revenue(df: pd.DataFrame, windows: list[int] | None = None) -> pd.DataFrame:
    """Add rolling mean revenue features per order, sorted by date.

    Args:
        df: Merged sales DataFrame.
        windows: Rolling window sizes in rows. Defaults to [7, 30].

    Returns:
        DataFrame with additional rolling_revenue_{w} columns.
    """
    if windows is None:
        windows = [7, 30]
    df = df.sort_values("Order Date").copy()
    for w in windows:
        df[f"rolling_revenue_{w}"] = df["Amount"].rolling(window=w, min_periods=1).mean()
    logger.debug("Added rolling revenue features for windows %s", windows)
    return df


def encode_categorical(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """One-hot encode categorical columns.

    Args:
        df: Input DataFrame.
        columns: Columns to encode. Defaults to ['Category', 'PaymentMode'].

    Returns:
        DataFrame with original columns replaced by one-hot dummies.
    """
    if columns is None:
        columns = ["Category", "PaymentMode"]
    existing = [c for c in columns if c in df.columns]
    if not existing:
        logger.warning("No matching columns found for encoding: %s", columns)
        return df
    df = pd.get_dummies(df, columns=existing, drop_first=False)
    logger.debug("One-hot encoded columns: %s", existing)
    return df


def add_profit_margin_feature(df: pd.DataFrame) -> pd.DataFrame:
    """Add a per-row profit margin column.

    Args:
        df: DataFrame with 'Amount' and 'Profit' columns.

    Returns:
        DataFrame with a new 'profit_margin' column (NaN where Amount == 0).
    """
    df = df.copy()
    df["profit_margin"] = np.where(df["Amount"] == 0, np.nan, df["Profit"] / df["Amount"])
    return df


def add_revenue_tier(df: pd.DataFrame, bins: list[float] | None = None) -> pd.DataFrame:
    """Assign each order to a revenue tier using quantile-based binning.

    Args:
        df: DataFrame with 'Amount' column.
        bins: Quantile edges (0–1). Defaults to [0, 0.33, 0.67, 1.0].

    Returns:
        DataFrame with a new 'revenue_tier' column: low / mid / high.
    """
    if bins is None:
        bins = [0.0, 0.33, 0.67, 1.0]
    df = df.copy()
    try:
        df["revenue_tier"] = pd.qcut(
            df["Amount"],
            q=bins,
            labels=["low", "mid", "high"],
            duplicates="drop",
        )
    except ValueError:
        df["revenue_tier"] = "unknown"
        logger.warning("Could not compute revenue tiers; assigned 'unknown'")
    return df
