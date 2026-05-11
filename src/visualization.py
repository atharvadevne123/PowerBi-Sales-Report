"""Chart generation utilities using matplotlib and seaborn."""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

matplotlib.use("Agg")

logger = logging.getLogger(__name__)


def save_revenue_by_category(df: pd.DataFrame, out_path: Path) -> Path:
    """Save a horizontal bar chart of revenue by category.

    Args:
        df: Merged sales DataFrame.
        out_path: Destination file path (.png).

    Returns:
        The resolved out_path.
    """
    rev = df.groupby("Category")["Amount"].sum().sort_values()
    fig, ax = plt.subplots(figsize=(8, 4))
    rev.plot(kind="barh", ax=ax, color="steelblue")
    ax.set_xlabel("Total Revenue (₹)")
    ax.set_title("Revenue by Category")
    plt.tight_layout()
    fig.savefig(out_path, dpi=100)
    plt.close(fig)
    logger.info("Saved revenue chart to %s", out_path)
    return out_path


def save_monthly_trend(df: pd.DataFrame, out_path: Path) -> Path:
    """Save a line chart of monthly revenue trend.

    Args:
        df: Merged sales DataFrame with 'Order Date'.
        out_path: Destination file path (.png).

    Returns:
        The resolved out_path.
    """
    df = df.copy()
    df["Month"] = df["Order Date"].dt.to_period("M")
    monthly = df.groupby("Month")["Amount"].sum()
    x_labels = [str(p) for p in monthly.index]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(x_labels, monthly.values, marker="o", linewidth=2, color="darkorange")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (₹)")
    ax.set_title("Monthly Revenue Trend")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    fig.savefig(out_path, dpi=100)
    plt.close(fig)
    logger.info("Saved monthly trend chart to %s", out_path)
    return out_path


def save_payment_mode_pie(df: pd.DataFrame, out_path: Path) -> Path:
    """Save a pie chart of orders by payment mode.

    Args:
        df: Merged sales DataFrame.
        out_path: Destination file path (.png).

    Returns:
        The resolved out_path.
    """
    dist = df["PaymentMode"].value_counts()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(dist.values, labels=dist.index, autopct="%1.1f%%", startangle=140)
    ax.set_title("Orders by Payment Mode")
    plt.tight_layout()
    fig.savefig(out_path, dpi=100)
    plt.close(fig)
    logger.info("Saved payment mode chart to %s", out_path)
    return out_path


def save_top_customers(df: pd.DataFrame, out_path: Path, n: int = 10) -> Path:
    """Save a bar chart of top-N customers by revenue.

    Args:
        df: Merged sales DataFrame.
        out_path: Destination file path (.png).
        n: Number of customers to display.

    Returns:
        The resolved out_path.
    """
    top = df.groupby("CustomerName")["Amount"].sum().nlargest(n).sort_values()
    fig, ax = plt.subplots(figsize=(8, 5))
    top.plot(kind="barh", ax=ax, color="mediumseagreen")
    ax.set_xlabel("Total Revenue (₹)")
    ax.set_title(f"Top {n} Customers by Revenue")
    plt.tight_layout()
    fig.savefig(out_path, dpi=100)
    plt.close(fig)
    logger.info("Saved top customers chart to %s", out_path)
    return out_path


def save_profit_heatmap(df: pd.DataFrame, out_path: Path) -> Path:
    """Save a heatmap of profit by category and payment mode.

    Args:
        df: Merged sales DataFrame.
        out_path: Destination file path (.png).

    Returns:
        The resolved out_path.
    """
    pivot = df.pivot_table(values="Profit", index="Category", columns="PaymentMode", aggfunc="sum", fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax)
    ax.set_title("Profit Heatmap: Category × Payment Mode")
    plt.tight_layout()
    fig.savefig(out_path, dpi=100)
    plt.close(fig)
    logger.info("Saved profit heatmap to %s", out_path)
    return out_path
