---
type: Playbook
title: Local Development Setup & Execution
description: Instructions for starting backing services, FastAPI server, Vite dev server, and running with Docker Compose.
status: stable
generated:
  by: okf-agent/gemini-2.5-pro
  at: 2026-09-16T13:14:03Z
verified:
  - by: human:leszekw
    at: 2026-09-16T13:20:00Z
sources:
  - id: dev-doc
    resource: baseline_repo/development.md
    title: Development Guide
    author: human:tiangolo
    last_modified: 2026-08-01T00:00:00Z
---

# Local Development Setup & Execution

Two workflows are supported for local development[^dev-doc]: Hybrid Local (FastAPI + Vite locally with Docker backing services) and Full Stack Docker Compose.

## Workflow A: Hybrid Local Setup (Recommended for Active Development)

### 1. Start Backing Infrastructure
From the repository root:
```bash
docker compose up -d db mailpit
```

### 2. Prepare Database and Launch Backend
From `./backend`:
```bash
uv sync
uv run bash scripts/prestart.sh
uv run fastapi dev
```
FastAPI runs on `http://localhost:8000` with Swagger UI at `http://localhost:8000/docs`.

### 3. Launch Frontend Development Server
In another terminal, from the project root:
```bash
bun install
bun run dev
```
Vite runs on `http://localhost:5173` and proxies backend requests to `http://localhost:8000`.

## Workflow B: Full Stack with Docker Compose

Run both frontend, backend, database, mailpit, adminer, and traefik via Docker Compose:
```bash
docker compose run --rm backend bash scripts/prestart.sh
docker compose watch
```

See [/services/stack_topology.md](/services/stack_topology.md) for full URL and port mappings.

[^dev-doc]: baseline_repo/development.md
