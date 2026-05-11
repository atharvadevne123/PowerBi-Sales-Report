"""Tests for src.validation schema checks."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.validation import validate_csv_path, validate_details_schema, validate_orders_schema


def test_validate_details_schema_valid(merged_df: pd.DataFrame) -> None:
    from src.data_loader import load_details

    details = load_details(Path(__file__).parent.parent / "Details.csv") if (Path(__file__).parent.parent / "Details.csv").exists() else merged_df
    errors = validate_details_schema(details)
    assert isinstance(errors, list)


def test_validate_details_schema_missing_column() -> None:
    df = pd.DataFrame({"Order ID": ["A"], "Amount": [100]})
    errors = validate_details_schema(df)
    assert any("Missing" in e for e in errors)


def test_validate_details_schema_negative_amount() -> None:
    df = pd.DataFrame(
        {
            "Order ID": ["A"],
            "Amount": [-100.0],
            "Profit": [10.0],
            "Quantity": [1],
            "Category": ["X"],
            "Sub-Category": ["Y"],
            "PaymentMode": ["COD"],
        }
    )
    errors = validate_details_schema(df)
    assert any("Negative" in e and "Amount" in e for e in errors)


def test_validate_orders_schema_missing_column() -> None:
    df = pd.DataFrame({"Order ID": ["A"], "CustomerName": ["Bob"]})
    errors = validate_orders_schema(df)
    assert any("Missing" in e for e in errors)


def test_validate_orders_schema_null_dates() -> None:
    df = pd.DataFrame(
        {
            "Order ID": ["A"],
            "Order Date": [None],
            "CustomerName": ["Bob"],
            "State": ["MH"],
            "City": ["Mumbai"],
        }
    )
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    errors = validate_orders_schema(df)
    assert any("null" in e.lower() for e in errors)


def test_validate_csv_path_not_found() -> None:
    errors = validate_csv_path(Path("/nonexistent/file.csv"), "test")
    assert len(errors) == 1
    assert "not found" in errors[0]


def test_validate_csv_path_wrong_extension(tmp_path: Path) -> None:
    p = tmp_path / "file.txt"
    p.write_text("hello")
    errors = validate_csv_path(p, "test")
    assert any(".csv" in e for e in errors)


def test_validate_csv_path_valid(tmp_path: Path) -> None:
    p = tmp_path / "data.csv"
    p.write_text("a,b\n1,2\n")
    errors = validate_csv_path(p, "test")
    assert errors == []
