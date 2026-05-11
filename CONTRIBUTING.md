# Contributing

## Getting Started

```bash
git clone https://github.com/atharvadevne123/PowerBi-Sales-Report
cd PowerBi-Sales-Report
pip install -r requirements.txt
pre-commit install
```

## Running Tests

```bash
make test
```

## Code Style

We use [ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
make lint       # check
make lint-fix   # auto-fix
```

## Pull Request Process

1. Fork the repository and create a feature branch.
2. Write or update tests for any changed behaviour.
3. Ensure `make test` and `make lint` pass.
4. Open a pull request with a clear description of the change.

## Reporting Issues

Open an issue on GitHub with a minimal reproducible example.
