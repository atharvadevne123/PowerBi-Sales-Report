"""Tests for src.visualization chart generators."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.visualization import (
    save_monthly_trend,
    save_payment_mode_pie,
    save_profit_heatmap,
    save_revenue_by_category,
    save_top_customers,
)


@pytest.fixture()
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Order Date": pd.to_datetime(["2023-01-10", "2023-02-15", "2023-03-20"]),
            "Amount": [1000.0, 500.0, 750.0],
            "Profit": [200.0, 100.0, 150.0],
            "Quantity": [5, 2, 3],
            "Category": ["Electronics", "Furniture", "Electronics"],
            "Sub-Category": ["Mobile", "Chairs", "Laptops"],
            "PaymentMode": ["COD", "UPI", "COD"],
            "CustomerName": ["Alice", "Bob", "Alice"],
            "State": ["Maharashtra", "Delhi", "Maharashtra"],
        }
    )


def test_save_revenue_by_category_creates_file(sample_df: pd.DataFrame, tmp_path: Path) -> None:
    out = tmp_path / "rev.png"
    result = save_revenue_by_category(sample_df, out)
    assert result == out
    assert out.exists()
    assert out.stat().st_size > 0


def test_save_monthly_trend_creates_file(sample_df: pd.DataFrame, tmp_path: Path) -> None:
    out = tmp_path / "trend.png"
    result = save_monthly_trend(sample_df, out)
    assert result.exists()


def test_save_payment_mode_pie_creates_file(sample_df: pd.DataFrame, tmp_path: Path) -> None:
    out = tmp_path / "pie.png"
    result = save_payment_mode_pie(sample_df, out)
    assert result.exists()


def test_save_top_customers_creates_file(sample_df: pd.DataFrame, tmp_path: Path) -> None:
    out = tmp_path / "top.png"
    result = save_top_customers(sample_df, out, n=2)
    assert result.exists()


def test_save_profit_heatmap_creates_file(sample_df: pd.DataFrame, tmp_path: Path) -> None:
    out = tmp_path / "heat.png"
    result = save_profit_heatmap(sample_df, out)
    assert result.exists()


@pytest.mark.parametrize("n", [1, 2, 3])
def test_save_top_customers_various_n(sample_df: pd.DataFrame, tmp_path: Path, n: int) -> None:
    out = tmp_path / f"top_{n}.png"
    result = save_top_customers(sample_df, out, n=n)
    assert result.exists()
