---
type: Configuration
title: Docker Compose Files & Inheritance
description: Architecture of compose.yml, compose.override.yml, and compose.deploy.yml configurations.
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
  - id: deploy-compose
    resource: baseline_repo/deployment-docker-compose.md
    title: Docker Compose Deployment Guide
    author: human:tiangolo
    last_modified: 2026-08-01T00:00:00Z
---

# Docker Compose Files & Inheritance

The project structures its container definitions across three tiered Compose files[^dev-doc]:

| Compose File | Purpose & Role | Invocation Mechanism |
|---|---|---|
| `compose.yml` | Base multi-service definition (db, backend, traefik, adminer, mailpit). Shared across all environments. | Automatically loaded by `docker compose` |
| `compose.override.yml` | Local development extensions (volume mounts for hot reload, port exposes, mailpit binding). | Automatically merged by default `docker compose` calls |
| `compose.deploy.yml` | Production deployment extensions: enables HTTPS, Let's Encrypt certificates, domain routing, and removes dev overrides. | Explicit flag: `docker compose -f compose.yml -f compose.deploy.yml` |

## Deployment Rule
To deploy to production without development volume bindings, pass both files explicitly:
```bash
docker compose -f compose.yml -f compose.deploy.yml up -d
```

See [/playbooks/production_deployment.md](/playbooks/production_deployment.md) and [/configurations/environment_variables.md](/configurations/environment_variables.md).

[^dev-doc]: baseline_repo/development.md
[^deploy-compose]: baseline_repo/deployment-docker-compose.md
