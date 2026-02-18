.PHONY: install test debug one-test format format-check lint all

install:
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

test:
	python -m pytest -vv \
		--cov=app \
		--cov-report=term-missing \
		--cov-fail-under=80

debug:
	python -m pytest -vv -x

# Run a single test by node id (file::test_name)
# Usage: make one-test T=test_app.py::test_hi_to_en_uses_hi_en_pipe
one-test:
	python -m pytest -vv "$(T)"

format:
	black *.py

format-check:
	black --check *.py

lint:
	pylint --disable=R,C,no-member app.py test_app.py

all: install lint format-check test
