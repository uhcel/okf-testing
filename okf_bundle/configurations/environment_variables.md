---
type: Configuration
title: Environment Variables & Secrets Reference
description: Complete listing of environment variables for local development, docker compose orchestration, and production TLS deployment.
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
  - id: deploy-compose
    resource: baseline_repo/deployment-docker-compose.md
    title: Docker Compose Deployment Guide
    author: human:tiangolo
    last_modified: 2026-08-01T00:00:00Z
---

# Environment Variables & Secrets Reference

Configuration settings are supplied via `.env` files and host shell environment variables[^dev-doc][^deploy-compose].

## Core Variables

| Variable | Scope | Description | Example |
|---|---|---|---|
| `DOMAIN` | Production / Compose | Host domain name for Traefik routing & Let's Encrypt TLS certificate generation | `fastapi-project.example.com` |
| `PROJECT_NAME` | Global | Human-readable title of the project | `"Full Stack FastAPI Project"` |
| `FIRST_SUPERUSER` | Database Initialization | Initial administrative user email | `admin@example.com` |
| `FASTAPI_ENV` | Runtime | Environment mode (`development`, `production`, `test`) | `development` |
| `ENVIRONMENT` | Compose / Sentry | Deployment environment tag | `production` |

## Secrets

| Secret Variable | Description | Generation Recommendation |
|---|---|---|
| `POSTGRES_PASSWORD` | Database password for PostgreSQL user | `python -c 'import secrets; print(secrets.token_urlsafe(32))'` |
| `SECRET_KEY` | JWT signing secret for backend authentication | `python -c 'import secrets; print(secrets.token_urlsafe(32))'` |
| `FIRST_SUPERUSER_PASSWORD` | Password for the initial administrator user | `python -c 'import secrets; print(secrets.token_urlsafe(32))'` |
| `SMTP_PASSWORD` | Optional password for authenticated external email delivery | Provider token or app password |

## Optional Integrations
- `SMTP_HOST`, `SMTP_USER`, `EMAILS_FROM_EMAIL`: External email routing parameters.
- `SENTRY_DSN`: Error reporting endpoint.

See [/configurations/docker_compose_files.md](/configurations/docker_compose_files.md) and [/playbooks/production_deployment.md](/playbooks/production_deployment.md).

[^dev-doc]: baseline_repo/development.md
[^deploy-compose]: baseline_repo/deployment-docker-compose.md
