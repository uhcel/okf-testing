---
type: Service
title: Backend API Service
description: Architecture and components of the FastAPI Python backend, SQLModel models, and Alembic migrations.
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
---

# Backend API Service

The backend is built with FastAPI and runs under Python 3.10+ using `uv`[^backend-readme].

## Code Organization
- `./backend/app/models.py`: SQLModel database models and Pydantic schemas.
- `./backend/app/api/`: API router endpoints organized by resource (login, users, items).
- `./backend/app/crud.py`: Database query utilities and CRUD operations.
- `./backend/app/core/db.py`: Database engine initialization and session management.
- `./backend/app/alembic/`: Database migration environment and version scripts.

## Interactive Documentation
Swagger UI documentation is served natively at `http://localhost:8000/docs`[^backend-readme].

See [/playbooks/database_migrations.md](/playbooks/database_migrations.md) and [/playbooks/backend_testing.md](/playbooks/backend_testing.md).

[^backend-readme]: baseline_repo/backend/README.md
