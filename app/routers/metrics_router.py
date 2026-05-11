"""APIRouter for business metrics endpoints."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/business-metrics", tags=["Business Metrics"])


def _get_df() -> Any:
    """Import the cached DataFrame from app.main."""
    from app.main import _get_df as _main_get_df

    return _main_get_df()


@router.get("/growth-rate")
async def growth_rate() -> dict[str, float]:
    """Return month-over-month revenue growth rate for the last period."""
    try:
        from src.metrics import revenue_growth_rate

        df = _get_df()
        rate = revenue_growth_rate(df)
        return {"growth_rate": round(rate, 6)}
    except Exception as exc:
        logger.error("growth-rate error: %s", exc)
        raise HTTPException(status_code=500, detail="Growth rate computation failed") from exc


@router.get("/retention")
async def retention(window_days: int = 90) -> dict[str, float]:
    """Return customer retention rate over the last N days."""
    if window_days <= 0:
        raise HTTPException(status_code=422, detail="window_days must be positive")
    try:
        from src.metrics import customer_retention_rate

        df = _get_df()
        rate = customer_retention_rate(df, window_days=window_days)
        return {"retention_rate": round(rate, 6), "window_days": window_days}
    except Exception as exc:
        logger.error("retention error: %s", exc)
        raise HTTPException(status_code=500, detail="Retention rate computation failed") from exc


@router.get("/gini")
async def gini(column: str = "Amount") -> dict[str, float]:
    """Return Gini coefficient for revenue concentration."""
    if column not in ("Amount", "Profit"):
        raise HTTPException(status_code=422, detail="column must be 'Amount' or 'Profit'")
    try:
        from src.metrics import gini_coefficient

        df = _get_df()
        g = gini_coefficient(df, column=column)
        return {"gini": g, "column": column}
    except Exception as exc:
        logger.error("gini error: %s", exc)
        raise HTTPException(status_code=500, detail="Gini computation failed") from exc


@router.get("/basket-size")
async def basket_size() -> dict[str, float]:
    """Return average number of line items per order."""
    try:
        from src.metrics import average_basket_size

        df = _get_df()
        avg = average_basket_size(df)
        return {"avg_basket_size": round(avg, 4)}
    except Exception as exc:
        logger.error("basket-size error: %s", exc)
        raise HTTPException(status_code=500, detail="Basket size computation failed") from exc
