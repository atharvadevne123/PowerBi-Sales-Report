"""Load and merge the Details and Orders CSV datasets."""

from __future__ import annotations

import logging
import os
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

DATA_DIR = Path(os.getenv("DATA_DIR", Path(__file__).parent.parent))


def load_details(path: Path | None = None) -> pd.DataFrame:
    """Load the order-details CSV and cast numeric columns.

    Args:
        path: Override path to Details.csv.

    Returns:
        DataFrame with typed columns.

    Raises:
        FileNotFoundError: If the CSV cannot be found.
        ValueError: If required columns are missing.
    """
    fpath = path or DATA_DIR / "Details.csv"
    if not fpath.exists():
        raise FileNotFoundError(f"Details CSV not found: {fpath}")

    df = pd.read_csv(fpath)
    required = {"Order ID", "Amount", "Profit", "Quantity", "Category", "Sub-Category", "PaymentMode"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Details.csv missing columns: {missing}")

    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df.dropna(subset=["Amount", "Profit", "Quantity"], inplace=True)
    logger.info("Loaded %d detail rows from %s", len(df), fpath)
    return df


def load_orders(path: Path | None = None) -> pd.DataFrame:
    """Load the orders CSV and parse order dates.

    Args:
        path: Override path to Orders.csv.

    Returns:
        DataFrame with a parsed 'Order Date' column.

    Raises:
        FileNotFoundError: If the CSV cannot be found.
        ValueError: If required columns are missing.
    """
    fpath = path or DATA_DIR / "Orders.csv"
    if not fpath.exists():
        raise FileNotFoundError(f"Orders CSV not found: {fpath}")

    df = pd.read_csv(fpath)
    required = {"Order ID", "Order Date", "CustomerName", "State", "City"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Orders.csv missing columns: {missing}")

    df["Order Date"] = pd.to_datetime(df["Order Date"], dayfirst=True, errors="coerce")
    df.dropna(subset=["Order Date"], inplace=True)
    logger.info("Loaded %d order rows from %s", len(df), fpath)
    return df


def load_merged(
    details_path: Path | None = None,
    orders_path: Path | None = None,
) -> pd.DataFrame:
    """Return Details and Orders merged on 'Order ID'.

    Args:
        details_path: Override path to Details.csv.
        orders_path: Override path to Orders.csv.

    Returns:
        Merged DataFrame.
    """
    details = load_details(details_path)
    orders = load_orders(orders_path)
    merged = details.merge(orders, on="Order ID", how="inner")
    logger.info("Merged dataset has %d rows", len(merged))
    return merged
