.PHONY: install test format lint format-check all

install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

test:
	python -m pytest -vv \
		--cov=calc \
		--cov-report=term-missing \
		--cov-fail-under=90

format:
	black calc tests

format-check:
	black --check calc tests

lint:
	pylint --disable=R,C calc tests

all: install lint format-check test
