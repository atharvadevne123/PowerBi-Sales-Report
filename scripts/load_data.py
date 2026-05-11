"""CLI script: print a summary of the loaded CSV data."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main(args: argparse.Namespace) -> None:
    """Print summary statistics to stdout."""
    from src.analysis import summary_stats
    from src.data_loader import load_merged

    df = load_merged(
        details_path=Path(args.details) if args.details else None,
        orders_path=Path(args.orders) if args.orders else None,
    )
    stats = summary_stats(df)
    print("\n=== Sales Data Summary ===")
    for key, val in stats.items():
        label = key.replace("_", " ").title()
        if key == "profit_margin":
            print(f"  {label}: {val:.1%}")
        elif isinstance(val, float):
            print(f"  {label}: ₹{val:,.2f}")
        else:
            print(f"  {label}: {val:,}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Print sales data summary")
    parser.add_argument("--details", default=None, help="Path to Details.csv")
    parser.add_argument("--orders", default=None, help="Path to Orders.csv")
    main(parser.parse_args())
