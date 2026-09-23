---
type: Service
title: Frontend Client Service
description: Architecture of the React Vite single-page application and its production integration with FastAPI.
status: stable
generated:
  by: okf-agent/gemini-2.5-pro
  at: 2026-09-16T13:14:03Z
verified:
  - by: human:uhcel
    at: 2026-09-16T13:20:00Z
sources:
  - id: dev-doc
    resource: baseline_repo/development.md
    title: Development Guide
    author: human:tiangolo
    last_modified: 2026-08-01T00:00:00Z
  - id: frontend-readme
    resource: baseline_repo/frontend/README.md
    title: Frontend Development Guide
    author: human:tiangolo
    last_modified: 2026-08-01T00:00:00Z
---

# Frontend Client Service

The frontend is a TypeScript Single Page Application (SPA) built with Vite, React, and Chakra UI / Tailwind[^frontend-readme].

## Development Mode
In development, the Vite dev server runs on `http://localhost:5173` via `bun run dev` and forwards API requests to `http://localhost:8000` via configuration in `frontend/.env`[^dev-doc].

## Production Build & Integration with FastAPI
To build the frontend for production:
```bash
bun run build
```
- **Output Destination**: The compiled static assets are written directly to `./backend/app/frontend`[^dev-doc].
- **Serving Mechanism**: The FastAPI application mounts and serves static files from `backend/app/frontend` at `http://localhost:8000` (root `/`).
- **Docker Compose Production**: In production Docker containers, the multi-stage backend Dockerfile automatically builds the frontend and copies the build into the container, eliminating the need to install Bun on production servers[^dev-doc].

See [/services/stack_topology.md](/services/stack_topology.md) and [/playbooks/local_development.md](/playbooks/local_development.md).

[^dev-doc]: baseline_repo/development.md
[^frontend-readme]: baseline_repo/frontend/README.md
