# 🚀 Continuous Integration with Python, Make & GitHub Actions

> CI pipeline using Pytest, coverage enforcement, Makefile automation, GitHub Actions, pre-commit hooks, and Docker.

[![CI](https://github.com/PawanKrGunjan/MLOps/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/PawanKrGunjan/MLOps/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![Coverage](https://img.shields.io/badge/Coverage-90%25-brightgreen)

---

## 📌 Overview

This repository demonstrates a **production-style CI pipeline** with quality gates:

- Automated testing (Pytest)
- Coverage enforcement (fails if total coverage drops below 90%)
- Linting (Pylint)
- Formatting validation (Black)
- Multi-version CI (Python 3.10 / 3.11 / 3.12)
- Pre-commit hooks for local validation
- Optional Docker workflow for reproducible runs

The GitHub Actions status badge uses the documented workflow-badge URL format. [web:2]

---

## 🏗 Architecture

```text
Developer
   │
   ▼
Pre-commit hooks (local)
   │
   ▼
Makefile (local CI)
   │
   ▼
GitHub Actions (remote CI)
   │
   ▼
Lint + Format + Tests + Coverage gate
   │
   ▼
Protected main branch
```

---

## 📂 Project Structure

> Note: GitHub Actions workflows must be stored at `.github/workflows/` in the **repo root**, which is why `ci.yml` lives outside `continuous-integration/`. [web:44]

```text
MLOps/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
└── continuous-integration/
    ├── calc/
    │   ├── __init__.py
    │   └── calculator.py
    ├── tests/
    │   └── test_calculator.py
    ├── Makefile
    ├── pyproject.toml
    ├── .pre-commit-config.yaml
    ├── Dockerfile
    ├── requirements.txt
    └── README.md
```

---

## 🧠 CI Layers

### 1️⃣ Local CI (Makefile)

Run the full local pipeline before pushing:

```bash
cd continuous-integration
make all
```

### 2️⃣ Remote CI (GitHub Actions)

Runs automatically when:

- Code is pushed to `dev` or `main`
- A Pull Request targets `main`

---

## 🛠 Makefile Targets

From `continuous-integration/`, run:

```bash
make <target>
```

Targets:

- `install`: Install dependencies
- `lint`: Run pylint checks
- `format`: Auto-format with Black
- `format-check`: Validate formatting (`black --check`)
- `test`: Run pytest + coverage gate (90%)
- `all`: Run full local CI (`install + lint + format-check + test`)

Coverage is enforced via `--cov-fail-under=90`. [web:27]

---

## 🌍 GitHub Actions CI

Workflow file location:

```text
.github/workflows/ci.yml
```

GitHub documents the workflow badge format as:

`https://github.com/OWNER/REPOSITORY/actions/workflows/WORKFLOW-FILE/badge.svg` [web:2]

---

## 🧪 Run Locally

```bash
cd continuous-integration
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

make install
make all
```

Push to trigger CI:

```bash
git push origin dev
```

---

## 🐳 Docker (Optional)

Build and run from `continuous-integration/`:

```bash
cd continuous-integration
docker build -t continuous-integration .
docker run --rm continuous-integration
```

---

## 🎯 What This Project Demonstrates

- Maintainable Python project structure (package + tests)
- CI-quality automation using Make targets
- Coverage gates to prevent untested changes
- Multi-version validation via GitHub Actions matrix
- Code quality enforcement with Pylint + Black
- A practical CI template you can reuse in MLOps projects
