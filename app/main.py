"""FastAPI application exposing the Sales Analytics REST API."""

from __future__ import annotations

import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator

import pandas as pd
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.models import (
    CategoryRevenueItem,
    DriftRequest,
    ForecastPoint,
    ForecastRequest,
    ForecastResponse,
    HealthResponse,
    MetricsResponse,
    SummaryResponse,
    TopCustomerItem,
)
from app.middleware import RateLimitMiddleware
from app.routers import metrics_router
from src import aggregations, analysis, data_loader, forecasting, monitoring

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

VERSION = "1.0.0"
_df_cache: dict[str, pd.DataFrame] = {}


def _get_df() -> pd.DataFrame:
    """Return the merged dataset, loading it on first call."""
    if "merged" not in _df_cache:
        _df_cache["merged"] = data_loader.load_merged()
    return _df_cache["merged"]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Pre-load dataset at startup."""
    try:
        _get_df()
        logger.info("Dataset loaded at startup")
    except Exception as exc:
        logger.warning("Could not pre-load dataset: %s", exc)
    yield


app = FastAPI(
    title="Sales Analytics API",
    description="REST API for PowerBi-Sales-Report: revenue, forecasting, drift detection.",
    version=VERSION,
    lifespan=lifespan,
)

app.include_router(metrics_router.router)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_correlation_id(request: Request, call_next: Any) -> Response:
    """Attach a correlation ID to every request for tracing."""
    correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    start = time.perf_counter()
    response: Response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Correlation-ID"] = correlation_id
    logger.info("%s %s %.1fms cid=%s", request.method, request.url.path, duration_ms, correlation_id)
    return response


@app.get("/health", response_model=HealthResponse, tags=["Operations"])
async def health() -> HealthResponse:
    """Return service health status."""
    return HealthResponse(status="ok", version=VERSION)


@app.get("/metrics", response_model=MetricsResponse, tags=["Operations"])
async def metrics() -> MetricsResponse:
    """Return basic dataset metrics."""
    try:
        df = _get_df()
        date_start = str(df["Order Date"].min().date()) if not df.empty else None
        date_end = str(df["Order Date"].max().date()) if not df.empty else None
        return MetricsResponse(
            total_rows=len(df),
            date_range_start=date_start,
            date_range_end=date_end,
        )
    except Exception as exc:
        logger.error("metrics error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to load metrics") from exc


@app.get("/version", tags=["Operations"])
async def version() -> dict[str, str]:
    """Return service version."""
    return {"version": VERSION}


@app.get("/summary", response_model=SummaryResponse, tags=["Analytics"])
async def summary() -> SummaryResponse:
    """Return high-level sales summary statistics."""
    try:
        df = _get_df()
        stats = analysis.summary_stats(df)
        return SummaryResponse(**stats)
    except Exception as exc:
        logger.error("summary error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to compute summary") from exc


@app.get("/revenue/category", response_model=list[CategoryRevenueItem], tags=["Analytics"])
async def revenue_by_category() -> list[CategoryRevenueItem]:
    """Return revenue broken down by product category."""
    try:
        df = _get_df()
        rev = analysis.revenue_by_category(df)
        return [CategoryRevenueItem(category=k, revenue=float(v)) for k, v in rev.items()]
    except Exception as exc:
        logger.error("revenue/category error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to compute category revenue") from exc


@app.get("/customers/top", response_model=list[TopCustomerItem], tags=["Analytics"])
async def top_customers(n: int = 10) -> list[TopCustomerItem]:
    """Return top-N customers by revenue.

    Args:
        n: Number of customers to return (1–50).
    """
    if not 1 <= n <= 50:
        raise HTTPException(status_code=422, detail="n must be between 1 and 50")
    try:
        df = _get_df()
        top = analysis.top_customers(df, n=n)
        return [TopCustomerItem(customer_name=k, revenue=float(v)) for k, v in top.items()]
    except Exception as exc:
        logger.error("customers/top error: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to compute top customers") from exc


@app.post("/forecast", response_model=ForecastResponse, tags=["Forecasting"])
async def forecast(body: ForecastRequest) -> ForecastResponse:
    """Forecast monthly revenue for the next N months."""
    try:
        df = _get_df()
        result = forecasting.forecast_revenue(df, horizon=body.horizon)
        points = [ForecastPoint(**row) for row in result.to_dict(orient="records")]
        return ForecastResponse(horizon=body.horizon, points=points)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("forecast error: %s", exc)
        raise HTTPException(status_code=500, detail="Forecast failed") from exc


@app.post("/drift", tags=["Monitoring"])
async def drift(body: DriftRequest) -> dict[str, Any]:
    """Detect distribution drift between a reference and current data window."""
    try:
        df = _get_df()
        df_sorted = df.sort_values("Order Date")
        cutoff = df_sorted["Order Date"].max() - pd.Timedelta(days=body.current_days)
        ref_cutoff = cutoff - pd.Timedelta(days=body.reference_days)
        reference = df_sorted[df_sorted["Order Date"] < cutoff]
        reference = reference[reference["Order Date"] >= ref_cutoff]
        current = df_sorted[df_sorted["Order Date"] >= cutoff]
        if reference.empty or current.empty:
            raise HTTPException(status_code=422, detail="Not enough data in specified windows")
        return monitoring.detect_drift(reference, current)
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("drift error: %s", exc)
        raise HTTPException(status_code=500, detail="Drift detection failed") from exc


@app.get("/report", tags=["Reports"])
async def download_report() -> FileResponse:
    """Generate and return a PDF sales report."""
    try:
        import tempfile

        from src import visualization
        from src.reporting import generate_report

        df = _get_df()
        stats = analysis.summary_stats(df)
        tmp_dir = Path(tempfile.mkdtemp())

        charts: list[Path] = []
        for fn, save_fn in [
            ("revenue_category.png", lambda p: visualization.save_revenue_by_category(df, p)),
            ("monthly_trend.png", lambda p: visualization.save_monthly_trend(df, p)),
            ("payment_mode.png", lambda p: visualization.save_payment_mode_pie(df, p)),
            ("top_customers.png", lambda p: visualization.save_top_customers(df, p)),
        ]:
            charts.append(save_fn(tmp_dir / fn))

        report_path = generate_report(stats, charts, out_path=tmp_dir / "report.pdf")
        return FileResponse(str(report_path), media_type="application/pdf", filename="sales_report.pdf")
    except Exception as exc:
        logger.error("report error: %s", exc)
        raise HTTPException(status_code=500, detail="Report generation failed") from exc


@app.get("/customers/clv", tags=["Analytics"])
async def customer_clv() -> list[dict[str, Any]]:
    """Return customer lifetime value metrics for all customers."""
    try:
        df = _get_df()
        clv = aggregations.customer_lifetime_value(df).reset_index()
        return clv.to_dict(orient="records")
    except Exception as exc:
        logger.error("customers/clv error: %s", exc)
        raise HTTPException(status_code=500, detail="CLV computation failed") from exc


@app.get("/revenue/quarterly", tags=["Analytics"])
async def quarterly_revenue() -> list[dict[str, Any]]:
    """Return revenue and profit aggregated by quarter."""
    try:
        df = _get_df()
        result = aggregations.quarterly_summary(df)
        return result.to_dict(orient="records")
    except Exception as exc:
        logger.error("revenue/quarterly error: %s", exc)
        raise HTTPException(status_code=500, detail="Quarterly revenue failed") from exc


@app.get("/subcategories/profitability", tags=["Analytics"])
async def subcategory_profitability() -> list[dict[str, Any]]:
    """Return revenue, profit, and margin for each sub-category."""
    try:
        df = _get_df()
        result = aggregations.subcategory_profitability(df)
        return result.to_dict(orient="records")
    except Exception as exc:
        logger.error("subcategories/profitability error: %s", exc)
        raise HTTPException(status_code=500, detail="Profitability computation failed") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")), reload=False)
