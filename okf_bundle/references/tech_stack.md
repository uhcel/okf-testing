---
type: Reference
title: Technology Stack & Core Tools
description: Overview of core technologies, runtimes, package managers, and libraries used across the full-stack template.
status: stable
generated:
  by: okf-agent/gemini-2.5-pro
  at: 2026-09-16T13:14:03Z
verified:
  - by: human:uhcel
    at: 2026-09-16T13:20:00Z
sources:
  - id: root-readme
    resource: baseline_repo/README.md
    title: Full Stack FastAPI Template Overview
    author: human:tiangolo
    last_modified: 2026-08-01T00:00:00Z
---

# Technology Stack

The project integrates modern backend and frontend runtimes and tools[^root-readme]:

| Domain | Technology | Purpose |
|---|---|---|
| Backend Framework | FastAPI | High-performance Python async web API |
| Backend Runtime / Tooling | `uv` | Python package and virtual environment manager |
| Database & ORM | PostgreSQL + SQLModel | Relational storage and Pydantic-based ORM |
| Database Migrations | Alembic | Schema versioning and migration automation |
| Frontend Framework | React + TypeScript | Single-page application UI |
| Frontend Tooling | Vite + Bun | Build tool, bundler, and JS package manager |
| Reverse Proxy | Traefik v3 | Routing, TLS termination, and Let's Encrypt certificates |
| Email Testing | Mailpit | Local development SMTP capture and web inspection |
| Admin Web UI | Adminer | Web-based database management interface |

See [/services/stack_topology.md](/services/stack_topology.md) for network port mappings and [/configurations/environment_variables.md](/configurations/environment_variables.md) for configuration.

[^root-readme]: baseline_repo/README.md
