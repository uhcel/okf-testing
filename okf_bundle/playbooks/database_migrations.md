---
type: Playbook
title: Database Migrations with Alembic
description: Step-by-step instructions and commands for generating and applying database migrations using Alembic and SQLModel.
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

# Database Migrations with Alembic

Every time data models change in `./backend/app/models.py`, generate a new Alembic revision and apply it to the PostgreSQL database[^backend-readme].

## Prerequisites
- PostgreSQL running (via Docker Compose: `docker compose up -d db`)[^backend-readme]
- Working directory: `./backend`

## 1. Create a Migration Revision
Run Alembic autogenerate from within `./backend` using `uv`:

```bash
uv run alembic revision --autogenerate -m "Add column last_name to User model"
```

Alembic automatically imports SQLModel schemas from `./backend/app/models.py` and creates a version script in `./backend/app/alembic/versions/`. Commit this script to Git.

## 2. Apply the Migration Locally
Execute the migration against PostgreSQL:

```bash
uv run alembic upgrade head
```

## 3. Alternative / Direct Table Creation (Optional)
If running without migrations in testing environments:
1. Uncomment `SQLModel.metadata.create_all(engine)` in `./backend/app/core/db.py`.
2. Comment out `alembic upgrade head` in `scripts/prestart.sh`.

See [/computations/apply_migrations.md](/computations/apply_migrations.md) for the attested computation specification.

[^backend-readme]: baseline_repo/backend/README.md
