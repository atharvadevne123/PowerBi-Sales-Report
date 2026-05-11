"""CLI script: detect drift between a reference and recent data window."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main(args: argparse.Namespace) -> None:
    """Print drift detection results to stdout."""
    import pandas as pd

    from src.data_loader import load_merged
    from src.monitoring import detect_drift

    df = load_merged(
        details_path=Path(args.details) if args.details else None,
        orders_path=Path(args.orders) if args.orders else None,
    )
    df = df.sort_values("Order Date")
    cutoff = df["Order Date"].max() - pd.Timedelta(days=args.current_days)
    ref_cutoff = cutoff - pd.Timedelta(days=args.reference_days)

    reference = df[(df["Order Date"] >= ref_cutoff) & (df["Order Date"] < cutoff)]
    current = df[df["Order Date"] >= cutoff]

    if reference.empty or current.empty:
        logger.error("Not enough data in the specified windows")
        return

    result = detect_drift(reference, current, alpha=args.alpha)
    print(json.dumps(result, indent=2))

    if result["drift_detected"]:
        logger.warning("DRIFT DETECTED in one or more columns!")
    else:
        logger.info("No significant drift detected.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect distribution drift in sales data")
    parser.add_argument("--details", default=None, help="Path to Details.csv")
    parser.add_argument("--orders", default=None, help="Path to Orders.csv")
    parser.add_argument("--reference-days", type=int, default=180, help="Days for reference window")
    parser.add_argument("--current-days", type=int, default=30, help="Days for current window")
    parser.add_argument("--alpha", type=float, default=0.05, help="Significance level")
    main(parser.parse_args())
