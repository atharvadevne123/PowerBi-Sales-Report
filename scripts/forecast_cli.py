"""CLI script: forecast monthly revenue and print results as a table."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main(args: argparse.Namespace) -> None:
    """Print the revenue forecast table to stdout."""
    from src.data_loader import load_merged
    from src.forecasting import forecast_revenue

    df = load_merged(
        details_path=Path(args.details) if args.details else None,
        orders_path=Path(args.orders) if args.orders else None,
    )
    result = forecast_revenue(df, horizon=args.horizon)
    print(f"\n{'Period':<12} {'Forecast':>12} {'Lower CI':>12} {'Upper CI':>12}")
    print("-" * 50)
    for _, row in result.iterrows():
        print(f"{row['period']:<12} {row['forecast']:>12,.2f} {row['lower_ci']:>12,.2f} {row['upper_ci']:>12,.2f}")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Forecast monthly revenue")
    parser.add_argument("--details", default=None, help="Path to Details.csv")
    parser.add_argument("--orders", default=None, help="Path to Orders.csv")
    parser.add_argument("--horizon", type=int, default=6, help="Months to forecast")
    main(parser.parse_args())
