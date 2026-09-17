---
type: Attested Computation
title: Apply Alembic Migrations Head
description: Blessed computation for running pending database migrations against PostgreSQL.
status: stable
runtime: bash
parameters:
  - { name: revision, type: string, required: false }
executor:
  resource: baseline_repo/backend/scripts/prestart.sh
  receipt: [exit_code, executed_command, output]
attester:
  resource: /references/attesters/exit_code_zero.py
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

# Computation

```bash
uv run alembic upgrade head
```

Applies all outstanding Alembic schema revisions to the active database engine[^backend-readme].

[^backend-readme]: baseline_repo/backend/README.md
