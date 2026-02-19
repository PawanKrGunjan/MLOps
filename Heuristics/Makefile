.PHONY: install test format lint refactor all clean help

install:
	@pip install --upgrade pip
	@pip install -r requirements.txt

test:
	@pytest -vv --cov=TSP --cov-report=term-missing --cov-report=html tests/

format:
	@black TSP/ tests/

lint:
	@pylint --disable=R,C --ignore-patterns='test_.*\.py' TSP tests

refactor: format lint

all: install lint test

clean:
	@rm -rf __pycache__ *.pyc *.pyo .pytest_cache htmlcov coverage.xml .coverage

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
