"""Tests for src.reporting PDF generation."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.reporting import generate_report


@pytest.fixture()
def sample_stats() -> dict:
    return {
        "total_orders": 100,
        "total_revenue": 250000.0,
        "total_profit": 50000.0,
        "total_quantity": 500,
        "profit_margin": 0.20,
        "avg_order_value": 2500.0,
    }


def test_generate_report_creates_pdf(sample_stats: dict, tmp_path: Path) -> None:
    out = tmp_path / "report.pdf"
    result = generate_report(sample_stats, [], out_path=out)
    assert result == out
    assert out.exists()
    assert out.stat().st_size > 0


def test_generate_report_with_no_charts(sample_stats: dict, tmp_path: Path) -> None:
    out = tmp_path / "report_no_charts.pdf"
    result = generate_report(sample_stats, [], out_path=out)
    assert result.exists()


def test_generate_report_uses_temp_path_when_none(sample_stats: dict) -> None:
    result = generate_report(sample_stats, [], out_path=None)
    assert result.exists()
    assert result.suffix == ".pdf"


def test_generate_report_skips_missing_chart(sample_stats: dict, tmp_path: Path) -> None:
    out = tmp_path / "report.pdf"
    missing = tmp_path / "nonexistent.png"
    result = generate_report(sample_stats, [missing], out_path=out)
    assert result.exists()


def test_generate_report_with_custom_timestamp(sample_stats: dict, tmp_path: Path) -> None:
    out = tmp_path / "report_ts.pdf"
    result = generate_report(sample_stats, [], out_path=out, generated_at="2026-01-01 00:00 UTC")
    assert result.exists()
