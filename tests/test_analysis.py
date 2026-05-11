"""Tests for src.analysis."""

from __future__ import annotations

import pandas as pd
import pytest

from src.analysis import (
    monthly_revenue,
    payment_mode_distribution,
    profit_by_subcategory,
    profit_margin,
    revenue_by_category,
    state_revenue,
    summary_stats,
    top_customers,
)


def test_revenue_by_category_sums_correctly(merged_df: pd.DataFrame) -> None:
    rev = revenue_by_category(merged_df)
    assert rev["Electronics"] == 1800


def test_revenue_by_category_sorted_desc(merged_df: pd.DataFrame) -> None:
    rev = revenue_by_category(merged_df)
    assert rev.is_monotonic_decreasing


def test_profit_by_subcategory_returns_series(merged_df: pd.DataFrame) -> None:
    profit = profit_by_subcategory(merged_df)
    assert isinstance(profit, pd.Series)
    assert len(profit) > 0


def test_top_customers_length(merged_df: pd.DataFrame) -> None:
    top = top_customers(merged_df, n=2)
    assert len(top) == 2


def test_top_customers_invalid_n(merged_df: pd.DataFrame) -> None:
    with pytest.raises(ValueError):
        top_customers(merged_df, n=0)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_top_customers_various_n(merged_df: pd.DataFrame, n: int) -> None:
    top = top_customers(merged_df, n=n)
    assert len(top) <= n


def test_monthly_revenue_returns_series(merged_df: pd.DataFrame) -> None:
    rev = monthly_revenue(merged_df)
    assert isinstance(rev, pd.Series)
    assert len(rev) > 0


def test_payment_mode_distribution_sums_to_total(merged_df: pd.DataFrame) -> None:
    dist = payment_mode_distribution(merged_df)
    assert dist.sum() == len(merged_df)


def test_profit_margin_between_zero_and_one(merged_df: pd.DataFrame) -> None:
    margin = profit_margin(merged_df)
    assert 0.0 <= margin <= 1.0


def test_profit_margin_zero_revenue() -> None:
    df = pd.DataFrame({"Amount": [0, 0], "Profit": [10, 20]})
    assert profit_margin(df) == 0.0


def test_state_revenue_sorted(merged_df: pd.DataFrame) -> None:
    sr = state_revenue(merged_df)
    assert sr.is_monotonic_decreasing


def test_summary_stats_keys(merged_df: pd.DataFrame) -> None:
    stats = summary_stats(merged_df)
    expected = {"total_orders", "total_revenue", "total_profit", "total_quantity", "profit_margin", "avg_order_value"}
    assert set(stats.keys()) == expected


def test_summary_stats_total_revenue(merged_df: pd.DataFrame) -> None:
    stats = summary_stats(merged_df)
    assert stats["total_revenue"] == pytest.approx(2650.0)


def test_summary_stats_total_orders(merged_df: pd.DataFrame) -> None:
    stats = summary_stats(merged_df)
    assert stats["total_orders"] == 5
