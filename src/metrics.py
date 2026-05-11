"""Business metrics computation for the sales analytics pipeline."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def revenue_growth_rate(df: pd.DataFrame) -> float:
    """Return the month-over-month revenue growth rate for the most recent period.

    Args:
        df: Merged sales DataFrame.

    Returns:
        Growth rate as a fraction (e.g. 0.05 = 5% growth). Returns 0.0 if
        fewer than 2 months of data exist.
    """
    df = df.copy()
    df["Month"] = df["Order Date"].dt.to_period("M")
    monthly = df.groupby("Month")["Amount"].sum().sort_index()
    if len(monthly) < 2:
        return 0.0
    prev, curr = monthly.iloc[-2], monthly.iloc[-1]
    if prev == 0:
        return 0.0
    return float((curr - prev) / prev)


def customer_retention_rate(df: pd.DataFrame, window_days: int = 30) -> float:
    """Estimate retention as fraction of repeat customers in the last window.

    Args:
        df: Merged sales DataFrame.
        window_days: Recent window in days to check for repeat customers.

    Returns:
        Fraction of customers who placed more than one order (0.0–1.0).
    """
    if window_days <= 0:
        raise ValueError("window_days must be positive")
    cutoff = df["Order Date"].max() - pd.Timedelta(days=window_days)
    recent = df[df["Order Date"] >= cutoff]
    if recent.empty:
        return 0.0
    order_counts = recent.groupby("CustomerName")["Order ID"].nunique()
    repeat = (order_counts > 1).sum()
    return float(repeat / len(order_counts))


def average_basket_size(df: pd.DataFrame) -> float:
    """Return the average number of line items per order.

    Args:
        df: Merged sales DataFrame.

    Returns:
        Float average lines per unique order.
    """
    if df.empty:
        return 0.0
    lines_per_order = df.groupby("Order ID").size()
    return float(lines_per_order.mean())


def gini_coefficient(df: pd.DataFrame, column: str = "Amount") -> float:
    """Compute the Gini coefficient for revenue concentration.

    Args:
        df: Merged sales DataFrame.
        column: Column to measure concentration for.

    Returns:
        Gini coefficient (0 = equal, 1 = max concentration).
    """
    values = df.groupby("CustomerName")[column].sum().values
    if len(values) == 0 or values.sum() == 0:
        return 0.0
    values = np.sort(values.astype(float))
    n = len(values)
    total = values.sum()
    gini = (2 * np.sum(np.arange(1, n + 1) * values) / (n * total)) - (n + 1) / n
    return float(round(max(0.0, gini), 6))
