"""Tests for src.data_loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.data_loader import load_details, load_merged, load_orders


def test_load_details_returns_dataframe(details_csv: Path) -> None:
    df = load_details(details_csv)
    assert len(df) == 5


def test_load_details_numeric_columns(details_csv: Path) -> None:
    df = load_details(details_csv)
    assert df["Amount"].dtype.kind == "f" or df["Amount"].dtype.kind == "i"
    assert df["Profit"].dtype.kind in ("f", "i")


def test_load_orders_parses_dates(orders_csv: Path) -> None:
    df = load_orders(orders_csv)
    import pandas as pd

    assert pd.api.types.is_datetime64_any_dtype(df["Order Date"])


def test_load_orders_row_count(orders_csv: Path) -> None:
    df = load_orders(orders_csv)
    assert len(df) == 5


def test_load_merged_joins_on_order_id(details_csv: Path, orders_csv: Path) -> None:
    df = load_merged(details_csv, orders_csv)
    assert "CustomerName" in df.columns
    assert "Amount" in df.columns
    assert len(df) == 5


def test_load_details_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_details(Path("/nonexistent/Details.csv"))


def test_load_orders_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_orders(Path("/nonexistent/Orders.csv"))


def test_load_details_missing_column_raises(tmp_path: Path) -> None:
    bad = tmp_path / "bad.csv"
    bad.write_text("Order ID,Amount\nX-001,100\n")
    with pytest.raises(ValueError, match="missing columns"):
        load_details(bad)


@pytest.mark.parametrize("amount,profit,quantity", [
    ("abc", "100", "1"),
    ("100", "xyz", "1"),
])
def test_load_details_drops_bad_numeric_rows(tmp_path: Path, amount: str, profit: str, quantity: str) -> None:
    p = tmp_path / "Details.csv"
    p.write_text(
        "Order ID,Amount,Profit,Quantity,Category,Sub-Category,PaymentMode\n"
        f"X-001,{amount},{profit},{quantity},Electronics,Mobile,COD\n"
        "X-002,500,100,2,Furniture,Chairs,UPI\n"
    )
    df = load_details(p)
    assert len(df) == 1
