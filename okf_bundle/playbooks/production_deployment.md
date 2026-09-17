---
type: Playbook
title: Production Deployment with Docker Compose & Traefik
description: Step-by-step procedure for building and deploying the full stack to production with Traefik TLS and Let's Encrypt.
status: stable
generated:
  by: okf-agent/gemini-2.5-pro
  at: 2026-09-16T13:14:03Z
verified:
  - by: human:leszekw
    at: 2026-09-16T13:20:00Z
sources:
  - id: deploy-compose
    resource: baseline_repo/deployment-docker-compose.md
    title: Docker Compose Deployment Guide
    author: human:tiangolo
    last_modified: 2026-08-01T00:00:00Z
---

# Production Deployment with Docker Compose & Traefik

Deploying to production requires combining `compose.yml` with `compose.deploy.yml` to enable HTTPS, Traefik reverse proxying, and automatic Let's Encrypt certificates while excluding local development overrides[^deploy-compose].

## 1. Configure Production Environment Variables
Export required environment variables and secrets on the host server:

```bash
export DOMAIN=fastapi-project.example.com
export PROJECT_NAME="Full Stack FastAPI Project"
export FIRST_SUPERUSER=admin@example.com

export POSTGRES_PASSWORD="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export FIRST_SUPERUSER_PASSWORD="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
```

## 2. Execute Deployment Commands
Run from the root project directory:

```bash
docker compose -f compose.yml -f compose.deploy.yml build
docker compose -f compose.yml -f compose.deploy.yml run --rm backend bash scripts/prestart.sh
docker compose -f compose.yml -f compose.deploy.yml up -d
```

## 3. Key Operational Details
- The backend Docker image automatically builds the frontend; Bun is not required on the server[^deploy-compose].
- Specifying both `-f compose.yml -f compose.deploy.yml` explicitly bypasses `compose.override.yml`.

See [/configurations/docker_compose_files.md](/configurations/docker_compose_files.md) and [/configurations/environment_variables.md](/configurations/environment_variables.md).

[^deploy-compose]: baseline_repo/deployment-docker-compose.md
