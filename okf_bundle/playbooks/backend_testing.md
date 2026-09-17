---
type: Playbook
title: Backend Testing & Coverage Execution
description: Commands and procedures for running backend pytest suites with coverage reporting locally and in Docker Compose.
status: stable
generated:
  by: okf-agent/gemini-2.5-pro
  at: 2026-09-16T13:14:03Z
verified:
  - by: human:leszekw
    at: 2026-09-16T13:20:00Z
sources:
  - id: backend-readme
    resource: baseline_repo/backend/README.md
    title: Backend Development Guide
    author: human:tiangolo
    last_modified: 2026-08-01T00:00:00Z
  - id: test-script
    resource: baseline_repo/backend/scripts/test.sh
    title: Test Runner Shell Script
    author: human:tiangolo
    last_modified: 2026-08-01T00:00:00Z
---

# Backend Testing & Coverage Execution

The backend test suite uses Pytest with coverage reporting configured in `scripts/test.sh`[^backend-readme][^test-script].

## 1. Running Tests Locally
From `./backend`:
```bash
uv run bash scripts/test.sh
```
This runs `FASTAPI_ENV=development coverage run -m pytest tests/`, prints a CLI coverage report, and generates an HTML report at `htmlcov/index.html`.

## 2. Running Tests in a Running Docker Compose Stack
If Docker Compose is already running:
```bash
docker compose exec backend bash scripts/tests-start.sh
```

To forward additional Pytest arguments (e.g., stop on first error `-x`):
```bash
docker compose exec backend bash scripts/tests-start.sh -x
```

## 3. Environment Variables for Tests
Tests execute with environment variables set by `.env` and `FASTAPI_ENV=development`[^test-script].

See [/computations/run_backend_tests.md](/computations/run_backend_tests.md) for the attested computation specification.

[^backend-readme]: baseline_repo/backend/README.md
[^test-script]: baseline_repo/backend/scripts/test.sh
