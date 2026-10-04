# Deployment Guide

## Prerequisites

- Docker & Docker Compose
- Python 3.12+ (local development)
- Node.js 22+ (frontend)
- Make (optional)

## Quick Start

```bash
cp .env.example .env
make up
make seed-users
make seed-invitro
```

## Services

| Service | Address | Description |
|-------|------|-------|
| API | http://localhost:8000 | FastAPI + OpenAPI `/docs` |
| Frontend | http://localhost:5173 | React (nginx proxy to the API) |
| PostgreSQL | localhost:5432 | `barekat` / `barekat` |
| Redis | localhost:6379 | Celery queue |
| MinIO | http://localhost:9000 | artifact store |
| MinIO Console | http://localhost:9001 | Panel |
| MLflow | http://localhost:5000 | Model training tracking |
| Qdrant | http://localhost:6333 | Molecule vector DB |
| Mosquitto MQTT | localhost:1883 | Lab robot commands |

## Users and Roles

```bash
make seed-users
```

| User | Password | Access |
|-------|-----|--------|
| admin | admin123 | compliance / audit / GDPR |
| scientist | scientist123 | synthetic, design, lab, predict (research) |
| clinician | clinician123 | predict |
| viewer | viewer123 | read |

## Migration and Seed

Migrations run automatically in the API entrypoint.

```bash
make migrate
make seed
make seed-users
make seed-invitro
```

## Local Development — Backend

```bash
cd backend
pip install -e ".[dev]"

# Windows (cmd)
set PYTHONPATH=%CD%;..\data

# Windows (PowerShell)
$env:PYTHONPATH="$PWD;..\data"

# Linux/macOS
export PYTHONPATH=$PWD:../data

uvicorn app.main:app --reload --port 8000
```

Or: `make dev` (the Makefile has been made compatible with PowerShell/cmd).

## Local Development — Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite proxies the `/api` path to `http://localhost:8000`.

## Health Check

```bash
curl http://localhost:8000/api/v1/health
```

```json
{
  "status": "ok",
  "version": "1.0.0",
  "auth_enabled": true,
  "services": {
    "database": "ok",
    "redis": "ok",
    "qdrant": "ok"
  }
}
```

## CI/CD

`.github/workflows/ci.yml`: lint + pytest (with Postgres/Redis) + build frontend + Docker images.

## Kubernetes / Terraform

```bash
kubectl apply -f infra/kubernetes/api-deployment.yaml
cd infra/terraform && terraform init && terraform plan
```

## Infrastructure Structure

```
infra/
├── docker-compose.yml
├── mosquitto.conf
├── kubernetes/api-deployment.yaml
└── terraform/
```
