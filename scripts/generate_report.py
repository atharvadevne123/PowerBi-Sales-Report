"""CLI script: generate a PDF sales report from the CSV data."""

from __future__ import annotations

import argparse
import logging
import tempfile
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main(args: argparse.Namespace) -> None:
    """Generate the PDF report and save it to the output path."""
    from src import visualization
    from src.analysis import summary_stats
    from src.data_loader import load_merged
    from src.reporting import generate_report

    logger.info("Loading data...")
    df = load_merged(
        details_path=Path(args.details) if args.details else None,
        orders_path=Path(args.orders) if args.orders else None,
    )
    stats = summary_stats(df)

    tmp_dir = Path(tempfile.mkdtemp())
    charts: list[Path] = [
        visualization.save_revenue_by_category(df, tmp_dir / "revenue_category.png"),
        visualization.save_monthly_trend(df, tmp_dir / "monthly_trend.png"),
        visualization.save_payment_mode_pie(df, tmp_dir / "payment_mode.png"),
        visualization.save_top_customers(df, tmp_dir / "top_customers.png"),
        visualization.save_profit_heatmap(df, tmp_dir / "profit_heatmap.png"),
    ]

    out = Path(args.output)
    generate_report(stats, charts, out_path=out)
    logger.info("Report saved to %s", out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate PDF sales report")
    parser.add_argument("--details", default=None, help="Path to Details.csv")
    parser.add_argument("--orders", default=None, help="Path to Orders.csv")
    parser.add_argument("--output", default="sales_report.pdf", help="Output PDF path")
    main(parser.parse_args())
