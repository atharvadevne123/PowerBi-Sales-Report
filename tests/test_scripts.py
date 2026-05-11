"""Tests for CLI scripts."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_load_data_script_runs(details_csv: Path, orders_csv: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/load_data.py",
            "--details", str(details_csv),
            "--orders", str(orders_csv),
        ],
        capture_output=True,
        text=True,
        cwd="/tmp/lantern-work/PowerBi-Sales-Report",
    )
    assert result.returncode == 0
    assert "Total Revenue" in result.stdout


def test_load_data_script_shows_profit_margin(details_csv: Path, orders_csv: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/load_data.py",
            "--details", str(details_csv),
            "--orders", str(orders_csv),
        ],
        capture_output=True,
        text=True,
        cwd="/tmp/lantern-work/PowerBi-Sales-Report",
    )
    assert "Profit Margin" in result.stdout


def test_generate_report_script_creates_pdf(details_csv: Path, orders_csv: Path, tmp_path: Path) -> None:
    out = tmp_path / "test_report.pdf"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_report.py",
            "--details", str(details_csv),
            "--orders", str(orders_csv),
            "--output", str(out),
        ],
        capture_output=True,
        text=True,
        cwd="/tmp/lantern-work/PowerBi-Sales-Report",
    )
    assert result.returncode == 0
    assert out.exists()
    assert out.stat().st_size > 0
