"""Core sales analysis functions over the merged dataset."""

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def revenue_by_category(df: pd.DataFrame) -> pd.Series:
    """Return total revenue grouped by Category.

    Args:
        df: Merged sales DataFrame.

    Returns:
        Series indexed by category, sorted descending.
    """
    result = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    logger.debug("revenue_by_category: %d categories", len(result))
    return result


def profit_by_subcategory(df: pd.DataFrame) -> pd.Series:
    """Return total profit grouped by Sub-Category.

    Args:
        df: Merged sales DataFrame.

    Returns:
        Series indexed by sub-category, sorted descending.
    """
    return df.groupby("Sub-Category")["Profit"].sum().sort_values(ascending=False)


def top_customers(df: pd.DataFrame, n: int = 10) -> pd.Series:
    """Return top-N customers by total revenue.

    Args:
        df: Merged sales DataFrame.
        n: Number of customers to return.

    Returns:
        Series indexed by CustomerName, values are total Amount.
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")
    return df.groupby("CustomerName")["Amount"].sum().nlargest(n)


def monthly_revenue(df: pd.DataFrame) -> pd.Series:
    """Return revenue aggregated by calendar month.

    Args:
        df: Merged sales DataFrame with 'Order Date' column.

    Returns:
        Series with Period index (monthly), values are total Amount.
    """
    df = df.copy()
    df["Month"] = df["Order Date"].dt.to_period("M")
    return df.groupby("Month")["Amount"].sum().sort_index()


def payment_mode_distribution(df: pd.DataFrame) -> pd.Series:
    """Return order count by payment mode.

    Args:
        df: Merged sales DataFrame.

    Returns:
        Series indexed by PaymentMode.
    """
    return df["PaymentMode"].value_counts()


def profit_margin(df: pd.DataFrame) -> float:
    """Return overall profit margin as a fraction.

    Args:
        df: Merged sales DataFrame.

    Returns:
        Profit / Amount ratio (0.0–1.0). Returns 0.0 if revenue is zero.
    """
    total_amount = df["Amount"].sum()
    if total_amount == 0:
        return 0.0
    return float(df["Profit"].sum() / total_amount)


def state_revenue(df: pd.DataFrame) -> pd.Series:
    """Return revenue aggregated by State.

    Args:
        df: Merged sales DataFrame.

    Returns:
        Series indexed by State, sorted descending.
    """
    return df.groupby("State")["Amount"].sum().sort_values(ascending=False)


def summary_stats(df: pd.DataFrame) -> dict[str, float | int]:
    """Return high-level summary statistics.

    Args:
        df: Merged sales DataFrame.

    Returns:
        Dict with keys: total_orders, total_revenue, total_profit,
        total_quantity, profit_margin, avg_order_value.
    """
    total_orders = int(df["Order ID"].nunique())
    total_revenue = float(df["Amount"].sum())
    total_profit = float(df["Profit"].sum())
    total_quantity = int(df["Quantity"].sum())
    margin = profit_margin(df)
    avg_order_value = total_revenue / total_orders if total_orders else 0.0
    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "total_quantity": total_quantity,
        "profit_margin": margin,
        "avg_order_value": avg_order_value,
    }
