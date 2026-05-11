"""Pytest fixtures for the Sales Analytics test suite."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def details_csv(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Write a minimal Details.csv to a temp directory."""
    p = tmp_path_factory.mktemp("data") / "Details.csv"
    p.write_text(
        "Order ID,Amount,Profit,Quantity,Category,Sub-Category,PaymentMode\n"
        "A-001,1000,300,5,Electronics,Mobile,COD\n"
        "A-002,500,100,2,Furniture,Chairs,UPI\n"
        "A-003,200,50,1,Clothing,Shirts,Credit Card\n"
        "A-004,800,200,4,Electronics,Laptops,EMI\n"
        "A-005,150,30,1,Clothing,Jeans,COD\n"
    )
    return p


@pytest.fixture(scope="session")
def orders_csv(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Write a minimal Orders.csv to a temp directory."""
    p = tmp_path_factory.mktemp("data") / "Orders.csv"
    p.write_text(
        "Order ID,Order Date,CustomerName,State,City\n"
        "A-001,01-01-2023,Alice,Maharashtra,Mumbai\n"
        "A-002,15-02-2023,Bob,Delhi,Delhi\n"
        "A-003,20-03-2023,Alice,Maharashtra,Pune\n"
        "A-004,05-04-2023,Charlie,Karnataka,Bangalore\n"
        "A-005,10-05-2023,Bob,Delhi,Delhi\n"
    )
    return p


@pytest.fixture(scope="session")
def merged_df(details_csv: Path, orders_csv: Path) -> pd.DataFrame:
    """Return the merged DataFrame from fixture CSVs."""
    from src.data_loader import load_merged

    return load_merged(details_path=details_csv, orders_path=orders_csv)


@pytest.fixture(scope="session")
def api_client(details_csv: Path, orders_csv: Path) -> TestClient:
    """Return a TestClient with the dataset pre-loaded from fixtures."""
    from app import main as app_module

    app_module._df_cache["merged"] = app_module.data_loader.load_merged(
        details_path=details_csv, orders_path=orders_csv
    )
    return TestClient(app)
