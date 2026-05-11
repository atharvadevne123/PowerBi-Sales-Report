"""Additional aggregation functions for multi-dimensional sales analysis."""

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def revenue_by_state_category(df: pd.DataFrame) -> pd.DataFrame:
    """Return a pivot table of revenue by State × Category.

    Args:
        df: Merged sales DataFrame.

    Returns:
        Pivot DataFrame with states as rows and categories as columns.
    """
    pivot = df.pivot_table(values="Amount", index="State", columns="Category", aggfunc="sum", fill_value=0.0)
    logger.debug("Computed revenue pivot: %d states × %d categories", *pivot.shape)
    return pivot


def quarterly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return revenue and profit aggregated by year-quarter.

    Args:
        df: Merged sales DataFrame with 'Order Date'.

    Returns:
        DataFrame with columns: quarter, revenue, profit, orders.
    """
    df = df.copy()
    df["quarter"] = df["Order Date"].dt.to_period("Q").astype(str)
    result = (
        df.groupby("quarter")
        .agg(revenue=("Amount", "sum"), profit=("Profit", "sum"), orders=("Order ID", "nunique"))
        .reset_index()
    )
    logger.debug("Quarterly summary: %d quarters", len(result))
    return result


def customer_lifetime_value(df: pd.DataFrame) -> pd.DataFrame:
    """Return CLV metrics per customer: total spend, orders, avg order, recency.

    Args:
        df: Merged sales DataFrame with 'Order Date' and 'CustomerName'.

    Returns:
        DataFrame indexed by CustomerName with clv, orders, avg_order, days_since_last columns.
    """
    max_date = df["Order Date"].max()
    clv = (
        df.groupby("CustomerName")
        .agg(
            clv=("Amount", "sum"),
            orders=("Order ID", "nunique"),
            last_order=("Order Date", "max"),
        )
        .assign(
            avg_order=lambda x: x["clv"] / x["orders"].clip(lower=1),
            days_since_last=lambda x: (max_date - x["last_order"]).dt.days,
        )
        .drop(columns=["last_order"])
        .sort_values("clv", ascending=False)
    )
    return clv


def subcategory_profitability(df: pd.DataFrame) -> pd.DataFrame:
    """Return margin and revenue for each Sub-Category.

    Args:
        df: Merged sales DataFrame.

    Returns:
        DataFrame with sub_category, revenue, profit, margin columns.
    """
    result = (
        df.groupby("Sub-Category")
        .agg(revenue=("Amount", "sum"), profit=("Profit", "sum"))
        .assign(margin=lambda x: x["profit"] / x["revenue"].clip(lower=1))
        .reset_index()
        .rename(columns={"Sub-Category": "sub_category"})
        .sort_values("revenue", ascending=False)
    )
    return result
