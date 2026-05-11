"""Tests for src.metrics business metrics."""

from __future__ import annotations

import pandas as pd
import pytest

from src.metrics import average_basket_size, customer_retention_rate, gini_coefficient, revenue_growth_rate


def test_revenue_growth_rate_insufficient_data(merged_df: pd.DataFrame) -> None:
    one_month = merged_df.copy()
    one_month["Order Date"] = pd.Timestamp("2023-01-15")
    result = revenue_growth_rate(one_month)
    assert result == 0.0


def test_revenue_growth_rate_positive_trend(merged_df: pd.DataFrame) -> None:
    result = revenue_growth_rate(merged_df)
    assert isinstance(result, float)


def test_customer_retention_rate_range(merged_df: pd.DataFrame) -> None:
    rate = customer_retention_rate(merged_df, window_days=365)
    assert 0.0 <= rate <= 1.0


def test_customer_retention_rate_invalid_window(merged_df: pd.DataFrame) -> None:
    with pytest.raises(ValueError):
        customer_retention_rate(merged_df, window_days=0)


def test_customer_retention_empty_window(merged_df: pd.DataFrame) -> None:
    rate = customer_retention_rate(merged_df, window_days=1)
    assert isinstance(rate, float)


def test_average_basket_size_positive(merged_df: pd.DataFrame) -> None:
    avg = average_basket_size(merged_df)
    assert avg > 0


def test_average_basket_size_empty() -> None:
    df = pd.DataFrame(columns=["Order ID", "CustomerName", "Amount"])
    assert average_basket_size(df) == 0.0


@pytest.mark.parametrize("column", ["Amount", "Profit"])
def test_gini_coefficient_range(merged_df: pd.DataFrame, column: str) -> None:
    g = gini_coefficient(merged_df, column=column)
    assert 0.0 <= g <= 1.0


def test_gini_coefficient_zero_revenue() -> None:
    df = pd.DataFrame({"CustomerName": ["A", "B"], "Amount": [0, 0]})
    assert gini_coefficient(df) == 0.0
