"""Tests for src.aggregations multi-dimensional analytics."""

from __future__ import annotations

import pandas as pd
import pytest

from src.aggregations import (
    customer_lifetime_value,
    quarterly_summary,
    revenue_by_state_category,
    subcategory_profitability,
)


def test_revenue_by_state_category_shape(merged_df: pd.DataFrame) -> None:
    pivot = revenue_by_state_category(merged_df)
    assert "Electronics" in pivot.columns or len(pivot.columns) > 0
    assert len(pivot) > 0


def test_revenue_by_state_category_no_negatives(merged_df: pd.DataFrame) -> None:
    pivot = revenue_by_state_category(merged_df)
    assert (pivot.values >= 0).all()


def test_quarterly_summary_columns(merged_df: pd.DataFrame) -> None:
    df = quarterly_summary(merged_df)
    assert "quarter" in df.columns
    assert "revenue" in df.columns
    assert "profit" in df.columns
    assert "orders" in df.columns


def test_quarterly_summary_revenue_positive(merged_df: pd.DataFrame) -> None:
    df = quarterly_summary(merged_df)
    assert (df["revenue"] >= 0).all()


def test_customer_lifetime_value_columns(merged_df: pd.DataFrame) -> None:
    clv = customer_lifetime_value(merged_df)
    assert "clv" in clv.columns
    assert "orders" in clv.columns
    assert "avg_order" in clv.columns
    assert "days_since_last" in clv.columns


def test_customer_lifetime_value_clv_positive(merged_df: pd.DataFrame) -> None:
    clv = customer_lifetime_value(merged_df)
    assert (clv["clv"] >= 0).all()


@pytest.mark.parametrize("customer", ["Alice", "Bob", "Charlie"])
def test_customer_lifetime_value_known_customers(merged_df: pd.DataFrame, customer: str) -> None:
    clv = customer_lifetime_value(merged_df)
    assert customer in clv.index


def test_subcategory_profitability_columns(merged_df: pd.DataFrame) -> None:
    prof = subcategory_profitability(merged_df)
    assert "sub_category" in prof.columns
    assert "revenue" in prof.columns
    assert "profit" in prof.columns
    assert "margin" in prof.columns


def test_subcategory_profitability_sorted_desc(merged_df: pd.DataFrame) -> None:
    prof = subcategory_profitability(merged_df)
    assert prof["revenue"].is_monotonic_decreasing
