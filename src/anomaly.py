"""Simple anomaly detection for sales metrics using z-score and IQR methods."""

from __future__ import annotations

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def zscore_anomalies(series: pd.Series, threshold: float = 3.0) -> pd.Series:
    """Flag values whose z-score exceeds the threshold.

    Args:
        series: Numeric pandas Series to analyse.
        threshold: Number of standard deviations to consider anomalous.

    Returns:
        Boolean Series; True where the value is anomalous.
    """
    if series.std() == 0:
        return pd.Series([False] * len(series), index=series.index)
    z = (series - series.mean()) / series.std(ddof=1)
    return z.abs() > threshold


def iqr_anomalies(series: pd.Series, multiplier: float = 1.5) -> pd.Series:
    """Flag values outside the IQR fence (Q1 - m*IQR, Q3 + m*IQR).

    Args:
        series: Numeric pandas Series.
        multiplier: IQR multiplier for the fence.

    Returns:
        Boolean Series; True where the value is anomalous.
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - multiplier * iqr
    upper = q3 + multiplier * iqr
    return (series < lower) | (series > upper)


def find_revenue_anomalies(
    df: pd.DataFrame,
    method: str = "zscore",
    threshold: float = 3.0,
) -> pd.DataFrame:
    """Return rows where order revenue is anomalous.

    Args:
        df: Merged sales DataFrame.
        method: 'zscore' or 'iqr'.
        threshold: Threshold for the chosen method.

    Returns:
        Subset of df containing anomalous rows, with 'anomaly_score' column.

    Raises:
        ValueError: If method is not 'zscore' or 'iqr'.
    """
    if method not in ("zscore", "iqr"):
        raise ValueError("method must be 'zscore' or 'iqr'")

    if method == "zscore":
        mask = zscore_anomalies(df["Amount"], threshold=threshold)
    else:
        mask = iqr_anomalies(df["Amount"], multiplier=threshold)

    anomalies = df[mask].copy()
    mean = df["Amount"].mean()
    anomalies["anomaly_score"] = (anomalies["Amount"] - mean).abs() / (df["Amount"].std(ddof=1) + 1e-9)
    logger.info("Found %d anomalous orders using %s method", len(anomalies), method)
    return anomalies
