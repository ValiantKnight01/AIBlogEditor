# Personal Blog Backend

Backend API for personal blog platform built with FastAPI.

## Setup

```bash
# Install dependencies
pip install -e ".[dev]"

# Run database migrations
alembic upgrade head

# Start development server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Testing

```bash
# Run all tests
pytest

# Run specific test types
pytest -m unit
pytest -m integration
pytest -m contract
pytest -m e2e

# Run with coverage
pytest --cov=src --cov-report=html
```

## Development

```bash
# Format code
black src tests
isort src tests

# Lint code
flake8 src tests
mypy src

# Run all checks
black src tests && isort src tests && flake8 src tests && mypy src
```