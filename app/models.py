"""Pydantic request/response models for the Sales Analytics API."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class ForecastRequest(BaseModel):
    """Request body for the /forecast endpoint."""

    horizon: int = Field(default=3, ge=1, le=24, description="Months ahead to forecast (1–24).")

    @field_validator("horizon")
    @classmethod
    def horizon_positive(cls, v: int) -> int:
        """Validate that horizon is a positive integer."""
        if v <= 0:
            raise ValueError("horizon must be >= 1")
        return v


class ForecastPoint(BaseModel):
    """A single forecast data point."""

    period: str
    forecast: float
    lower_ci: float
    upper_ci: float


class ForecastResponse(BaseModel):
    """Response for the /forecast endpoint."""

    horizon: int
    points: list[ForecastPoint]


class SummaryResponse(BaseModel):
    """Response for the /summary endpoint."""

    total_orders: int
    total_revenue: float
    total_profit: float
    total_quantity: int
    profit_margin: float
    avg_order_value: float


class CategoryRevenueItem(BaseModel):
    """Single category revenue record."""

    category: str
    revenue: float


class TopCustomerItem(BaseModel):
    """Single top-customer record."""

    customer_name: str
    revenue: float


class DriftRequest(BaseModel):
    """Request body for the /drift endpoint."""

    reference_days: int = Field(
        default=180,
        ge=7,
        le=730,
        description="Days of history to use as reference window.",
    )
    current_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Most-recent days to compare against the reference.",
    )


class HealthResponse(BaseModel):
    """Response for the /health endpoint."""

    status: str
    version: str


class MetricsResponse(BaseModel):
    """Response for the /metrics endpoint."""

    total_rows: int
    date_range_start: str | None
    date_range_end: str | None
