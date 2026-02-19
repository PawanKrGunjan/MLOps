.PHONY: install test format format-check lint refactor all clean help

# Install all dependencies
install:
	@pip install --upgrade pip
	@pip install -r requirements.txt

# Run tests with coverage
test:
	@pytest -vv --cov=TSP --cov-report=term-missing --cov-report=html tests/

# Autoformat code
format:
	@black TSP/ tests/

# Check code formatting (non-destructive)
format-check:
	@black --check TSP/ tests/

# Lint Python code
lint:
	@pylint --disable=R,C --ignore-patterns='test_.*\.py' TSP tests

# Format + lint
refactor: format lint

# Full pipeline: install, format, check, lint, test, clean
all: install format format-check lint test clean

# Remove caches and coverage reports
clean:
	@rm -rf __pycache__ *.pyc *.pyo .pytest_cache htmlcov coverage.xml .coverage

# Show help for each target
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
