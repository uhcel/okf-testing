---
type: Service
title: Stack Topology & Port Mappings
description: Complete network architecture, exposed localhost ports, internal communication, and service endpoints across development and Docker Compose.
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

# Stack Topology & Port Mappings

The application stack comprises multiple services exposed locally for development and orchestration[^dev-doc]:

| Service | Container / Process | Port (Host) | Access URL | Description |
|---|---|---|---|---|
| Backend API | `backend` (FastAPI) | `8000` | `http://localhost:8000` | REST API endpoints and static frontend serving |
| Swagger UI | `backend` (FastAPI) | `8000` | `http://localhost:8000/docs` | Interactive OpenAPI documentation |
| Frontend Dev | Vite Dev Server | `5173` | `http://localhost:5173` | Hot-reloading React frontend in local mode |
| Database | `db` (PostgreSQL) | `5432` | `localhost:5432` | PostgreSQL relational database |
| Mailpit Web UI | `mailpit` | `8025` | `http://localhost:8025` | Web dashboard to inspect captured development emails |
| Mailpit SMTP | `mailpit` | `1025` | `localhost:1025` | SMTP server endpoint capturing outgoing emails |
| Adminer | `adminer` | `8080` | `http://localhost:8080` | Web administration UI for database management |
| Traefik Proxy | `traefik` | `8090` | `http://localhost:8090` | Traefik dashboard displaying routing rules and TLS status |

In production mode, Traefik handles incoming traffic on ports `80` (HTTP) and `443` (HTTPS), automatically terminating TLS certificates via Let's Encrypt[^dev-doc].

See [/services/backend_api.md](/services/backend_api.md) and [/services/frontend_client.md](/services/frontend_client.md).

[^dev-doc]: baseline_repo/development.md
