PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
HOST ?= http://127.0.0.1:8000
LOCUST_FILE := Testing/locustfile.py

.PHONY: help install run locust locust-headless freeze clean test format lint format-check all

help:
	@echo "Available commands:"
	@echo "  make install          Install dependencies"
	@echo "  make run              Start FastAPI application"
	@echo "  make locust           Start Locust web UI"
	@echo "  make locust-headless  Run headless load test"
	@echo "  make freeze           Export installed packages"
	@echo "  make clean            Remove Python cache files"

install:
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

locust:
	$(PYTHON) -m locust -f $(LOCUST_FILE) --host $(HOST)

locust-headless:
	$(PYTHON) -m locust -f $(LOCUST_FILE) \
		--host $(HOST) \
		--headless \
		-u 10 \
		-r 2 \
		-t 60s

freeze:
	$(PIP) freeze > requirements.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test:
	$(PYTHON) -m pytest

format:
	$(PYTHON) -m black .

format-check:
	$(PYTHON) -m black --check .

lint:
	$(PYTHON) -m ruff check .

all: format-check lint test