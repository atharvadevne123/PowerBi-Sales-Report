.PHONY: install test lint type-check run docker-build docker-up clean

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --tb=short --cov=src --cov=app --cov-report=term-missing

lint:
	ruff check . --select E,F,W,I --ignore E501

lint-fix:
	ruff check . --select E,F,W,I --ignore E501 --fix

type-check:
	mypy src/ app/ --ignore-missing-imports

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -t powerbi-sales-report .

docker-up:
	docker-compose up --build

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache coverage.xml
