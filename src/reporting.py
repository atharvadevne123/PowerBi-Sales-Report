"""PDF report generation using fpdf2."""

from __future__ import annotations

import logging
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from fpdf import FPDF

logger = logging.getLogger(__name__)


class SalesReport(FPDF):
    """Multi-page PDF sales report."""

    def header(self) -> None:
        """Render the page header."""
        self.set_font("Helvetica", "B", 14)
        self.set_fill_color(30, 60, 120)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "Sales Analytics Report", new_x="LMARGIN", new_y="NEXT", fill=True)
        self.set_text_color(0, 0, 0)
        self.ln(3)

    def footer(self) -> None:
        """Render the page footer with page number."""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def generate_report(
    stats: dict[str, Any],
    chart_paths: list[Path],
    out_path: Path | None = None,
    generated_at: str | None = None,
) -> Path:
    """Generate a PDF report from summary stats and chart images.

    Args:
        stats: Dict from analysis.summary_stats().
        chart_paths: List of PNG paths to embed as pages.
        out_path: Output file path; uses a temp file if None.
        generated_at: Timestamp string; defaults to now.

    Returns:
        Path to the generated PDF.
    """
    if out_path is None:
        fd, tmp = tempfile.mkstemp(suffix=".pdf", prefix="sales_report_")
        out_path = Path(tmp)

    ts = generated_at or datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    pdf = SalesReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Generated: {ts}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Executive Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)

    labels = {
        "total_orders": "Total Orders",
        "total_revenue": "Total Revenue (₹)",
        "total_profit": "Total Profit (₹)",
        "total_quantity": "Units Sold",
        "profit_margin": "Profit Margin",
        "avg_order_value": "Avg Order Value (₹)",
    }
    for key, label in labels.items():
        val = stats.get(key, "N/A")
        if key == "profit_margin" and isinstance(val, float):
            val = f"{val:.1%}"
        elif isinstance(val, float):
            val = f"{val:,.2f}"
        pdf.cell(0, 7, f"  {label}: {val}", new_x="LMARGIN", new_y="NEXT")

    for chart in chart_paths:
        if not chart.exists():
            logger.warning("Chart not found, skipping: %s", chart)
            continue
        pdf.add_page()
        pdf.image(str(chart), x=10, w=190)

    pdf.output(str(out_path))
    logger.info("PDF report written to %s", out_path)
    return out_path
