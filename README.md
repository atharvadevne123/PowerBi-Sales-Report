# PowerBi-Sales-Report

[![CI](https://github.com/atharvadevne123/PowerBi-Sales-Report/actions/workflows/ci.yml/badge.svg)](https://github.com/atharvadevne123/PowerBi-Sales-Report/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Power BI sales analytics platform with a Python REST API for revenue analysis, forecasting, and drift detection.

This project uses Power BI to visualize sales performance across categories, customers, and time. It highlights profit, quantity, and revenue trends, with insights on top products, customer contributions, and seasonal fluctuations, enabling quick business decisions through interactive dashboards.

A Python analytics layer built on top of the raw CSV data provides:

- **FastAPI REST API** — summary stats, category revenue, top customers, forecasting, drift detection, PDF report download
- **OLS Revenue Forecasting** — linear trend model with 95% confidence intervals
- **KS-Test Drift Detection** — detect distribution shift between reference and current data windows
- **PDF Report Generation** — downloadable multi-page report with embedded charts

---

## Dashboard

<img width="1342" height="752" alt="Dashboard" src="https://github.com/user-attachments/assets/406f40d0-e752-4bd4-85b8-aed2d1b364a8" />

---

## Quick Start

```bash
git clone https://github.com/atharvadevne123/PowerBi-Sales-Report
cd PowerBi-Sales-Report
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive API docs.

### Docker

```bash
docker-compose up --build
```

### CLI Scripts

```bash
# Print summary statistics
python scripts/load_data.py

# Generate PDF report
python scripts/generate_report.py --output report.pdf
```

---

## API Reference

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health status |
| GET | `/version` | API version |
| GET | `/metrics` | Dataset row count and date range |
| GET | `/summary` | Total revenue, profit, orders, margin |
| GET | `/revenue/category` | Revenue by product category |
| GET | `/customers/top?n=10` | Top-N customers by revenue |
| POST | `/forecast` | Revenue forecast (OLS trend) |
| POST | `/drift` | KS-test drift detection |
| GET | `/report` | Download PDF sales report |

### Forecast Request

```json
POST /forecast
{
  "horizon": 6
}
```

```json
{
  "horizon": 6,
  "points": [
    {"period": "2018-05", "forecast": 85432.10, "lower_ci": 71200.00, "upper_ci": 99664.20}
  ]
}
```

---

## Architecture

```
PowerBi-Sales-Report/
├── Details.csv          # Order details (amount, profit, category)
├── Orders.csv           # Order headers (date, customer, state)
├── src/
│   ├── data_loader.py   # CSV loading and merging
│   ├── analysis.py      # Revenue, profit, customer analytics
│   ├── forecasting.py   # OLS trend forecasting
│   ├── monitoring.py    # KS-test drift detection
│   ├── visualization.py # Matplotlib chart generators
│   └── reporting.py     # PDF report (fpdf2)
├── app/
│   ├── main.py          # FastAPI app, endpoints, middleware
│   └── models.py        # Pydantic request/response models
├── tests/               # 60 tests (pytest)
├── scripts/             # CLI utilities
└── .github/workflows/   # CI (ruff + pytest + mypy)
```

---

## Setup

### Prerequisites

- Python 3.10+
- `pip install -r requirements.txt`

### Environment Variables

Copy `.env.example` to `.env` and set:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_DIR` | `.` | Directory containing `Details.csv` and `Orders.csv` |
| `PORT` | `8000` | API server port |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

## Testing

```bash
make test
# or
pytest tests/ -v --cov=src --cov=app
```

60 tests cover data loading, analysis functions, forecasting, drift detection, and all API endpoints.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, code style, and pull request guidelines.

## License

[MIT](LICENSE)
