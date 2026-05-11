"""Tests for src.features engineering pipeline."""

from __future__ import annotations

import pandas as pd
import pytest

from src.features import (
    add_profit_margin_feature,
    add_revenue_tier,
    add_rolling_revenue,
    add_time_features,
    encode_categorical,
)


@pytest.fixture()
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Order Date": pd.to_datetime(["2023-01-10", "2023-02-15", "2023-03-20", "2023-03-25"]),
            "Amount": [1000.0, 500.0, 750.0, 200.0],
            "Profit": [200.0, 100.0, 150.0, 40.0],
            "Category": ["Electronics", "Furniture", "Electronics", "Clothing"],
            "PaymentMode": ["COD", "UPI", "COD", "EMI"],
        }
    )


def test_add_time_features_year(sample_df: pd.DataFrame) -> None:
    df = add_time_features(sample_df)
    assert "year" in df.columns
    assert df["year"].iloc[0] == 2023


def test_add_time_features_month(sample_df: pd.DataFrame) -> None:
    df = add_time_features(sample_df)
    assert "month" in df.columns
    assert df["month"].iloc[0] == 1


def test_add_time_features_is_weekend(sample_df: pd.DataFrame) -> None:
    df = add_time_features(sample_df)
    assert "is_weekend" in df.columns
    assert df["is_weekend"].isin([0, 1]).all()


@pytest.mark.parametrize("col", ["year", "month", "quarter", "day_of_week", "is_weekend", "week_of_year"])
def test_add_time_features_all_columns(sample_df: pd.DataFrame, col: str) -> None:
    df = add_time_features(sample_df)
    assert col in df.columns


def test_add_rolling_revenue_default_windows(sample_df: pd.DataFrame) -> None:
    df = add_rolling_revenue(sample_df)
    assert "rolling_revenue_7" in df.columns
    assert "rolling_revenue_30" in df.columns


def test_add_rolling_revenue_custom_window(sample_df: pd.DataFrame) -> None:
    df = add_rolling_revenue(sample_df, windows=[3])
    assert "rolling_revenue_3" in df.columns


def test_encode_categorical_creates_dummies(sample_df: pd.DataFrame) -> None:
    df = encode_categorical(sample_df, columns=["Category"])
    assert "Category_Electronics" in df.columns or any("Electronics" in c for c in df.columns)


def test_encode_categorical_missing_column(sample_df: pd.DataFrame) -> None:
    df = encode_categorical(sample_df, columns=["NonExistentCol"])
    assert "NonExistentCol" not in df.columns


def test_add_profit_margin_feature(sample_df: pd.DataFrame) -> None:
    df = add_profit_margin_feature(sample_df)
    assert "profit_margin" in df.columns
    assert (df["profit_margin"] > 0).all()


def test_add_profit_margin_zero_amount() -> None:
    df = pd.DataFrame({"Amount": [0.0, 100.0], "Profit": [0.0, 20.0]})
    result = add_profit_margin_feature(df)
    import numpy as np

    assert np.isnan(result["profit_margin"].iloc[0])


def test_add_revenue_tier_creates_column(sample_df: pd.DataFrame) -> None:
    df = add_revenue_tier(sample_df)
    assert "revenue_tier" in df.columns
