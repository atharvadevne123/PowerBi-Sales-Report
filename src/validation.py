"""Input validation utilities for the sales analytics pipeline."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

_REQUIRED_DETAILS_COLS = {"Order ID", "Amount", "Profit", "Quantity", "Category", "Sub-Category", "PaymentMode"}
_REQUIRED_ORDERS_COLS = {"Order ID", "Order Date", "CustomerName", "State", "City"}


def validate_details_schema(df: pd.DataFrame) -> list[str]:
    """Return a list of schema validation errors for the Details DataFrame.

    Args:
        df: DataFrame to validate.

    Returns:
        List of error messages. Empty list means the schema is valid.
    """
    errors: list[str] = []
    missing = _REQUIRED_DETAILS_COLS - set(df.columns)
    if missing:
        errors.append(f"Missing columns: {sorted(missing)}")
    if "Amount" in df.columns and (df["Amount"] < 0).any():
        errors.append("Negative values found in 'Amount'")
    if "Quantity" in df.columns and (df["Quantity"] < 0).any():
        errors.append("Negative values found in 'Quantity'")
    return errors


def validate_orders_schema(df: pd.DataFrame) -> list[str]:
    """Return a list of schema validation errors for the Orders DataFrame.

    Args:
        df: DataFrame to validate.

    Returns:
        List of error messages. Empty list means the schema is valid.
    """
    errors: list[str] = []
    missing = _REQUIRED_ORDERS_COLS - set(df.columns)
    if missing:
        errors.append(f"Missing columns: {sorted(missing)}")
    if "Order Date" in df.columns:
        null_dates = df["Order Date"].isna().sum()
        if null_dates > 0:
            errors.append(f"{null_dates} null 'Order Date' values")
    return errors


def validate_csv_path(path: Path, name: str = "file") -> list[str]:
    """Validate that a CSV path exists and has the .csv extension.

    Args:
        path: Path to validate.
        name: Human-readable name for error messages.

    Returns:
        List of error messages.
    """
    errors: list[str] = []
    if not path.exists():
        errors.append(f"{name} not found: {path}")
    elif path.suffix.lower() != ".csv":
        errors.append(f"{name} must be a .csv file, got: {path.suffix}")
    return errors
