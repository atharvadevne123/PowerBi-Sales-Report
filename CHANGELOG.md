# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2026-05-11

### Added
- Python analytics layer: `src/data_loader.py`, `src/analysis.py`, `src/forecasting.py`, `src/visualization.py`, `src/monitoring.py`, `src/reporting.py`
- FastAPI REST API with endpoints: `/health`, `/metrics`, `/version`, `/summary`, `/revenue/category`, `/customers/top`, `/forecast`, `/drift`, `/report`
- OLS revenue forecasting with 95% confidence intervals
- KS-test drift detection for Amount, Profit, and Quantity distributions
- PDF report generation with embedded charts (fpdf2)
- Full test suite: 60 tests across data loading, analysis, forecasting, drift, and API
- GitHub Actions CI: lint (ruff), test, coverage, type-check (mypy)
- Dockerfile and docker-compose
- Pre-commit hooks, Makefile, pyproject.toml, .env.example
