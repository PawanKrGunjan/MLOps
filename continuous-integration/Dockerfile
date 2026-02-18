# =========================
# Base image
# =========================
FROM python:3.12-slim

# =========================
# Set work directory
# =========================
WORKDIR /app

# =========================
# Install system dependencies
# =========================
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# =========================
# Copy project files
# =========================
COPY pyproject.toml .
COPY requirements.txt .
COPY calc/ ./calc
COPY tests/ ./tests

# =========================
# Create virtual environment at ~/.venv
# =========================
RUN python -m venv /root/.venv

# Activate the venv and install dependencies
ENV PATH="/root/.venv/bin:$PATH"
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# =========================
# Default command: run tests with coverage
# =========================
CMD ["pytest", "-vv", "--cov=calc", "--cov-report=term-missing", "--cov-fail-under=90"]

