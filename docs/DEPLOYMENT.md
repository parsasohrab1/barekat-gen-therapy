# راهنمای استقرار

## پیش‌نیازها

- Docker & Docker Compose
- Python 3.12+ (توسعه محلی)
- Node.js 22+ (frontend)
- Make (اختیاری)

## راه‌اندازی سریع

```bash
cp .env.example .env
make up
make seed-users
make seed-invitro
```

## سرویس‌ها

| سرویس | آدرس | توضیح |
|-------|------|-------|
| API | http://localhost:8000 | FastAPI + OpenAPI `/docs` |
| Frontend | http://localhost:5173 | React (nginx proxy به API) |
| PostgreSQL | localhost:5432 | `barekat` / `barekat` |
| Redis | localhost:6379 | صف Celery |
| MinIO | http://localhost:9000 | artifact store |
| MinIO Console | http://localhost:9001 | پنل |
| MLflow | http://localhost:5000 | tracking آموزش مدل |
| Qdrant | http://localhost:6333 | vector DB مولکول‌ها |
| Mosquitto MQTT | localhost:1883 | دستورات ربات آزمایشگاه |

## کاربران و نقش‌ها

```bash
make seed-users
```

| کاربر | رمز | دسترسی |
|-------|-----|--------|
| admin | admin123 | compliance / audit / GDPR |
| scientist | scientist123 | synthetic, design, lab, predict (تحقیق) |
| clinician | clinician123 | predict |
| viewer | viewer123 | خواندن |

## Migration و Seed

Migrationها در entrypoint API خودکار اجرا می‌شوند.

```bash
make migrate
make seed
make seed-users
make seed-invitro
```

## توسعه محلی — Backend

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

یا: `make dev` (Makefile برای PowerShell/cmd سازگار شده).

## توسعه محلی — Frontend

```bash
cd frontend
npm install
npm run dev
```

Vite مسیر `/api` را به `http://localhost:8000` پروکسی می‌کند.

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

`.github/workflows/ci.yml`: lint + pytest (با Postgres/Redis) + build frontend + Docker images.

## Kubernetes / Terraform

```bash
kubectl apply -f infra/kubernetes/api-deployment.yaml
cd infra/terraform && terraform init && terraform plan
```

## ساختار زیرساخت

```
infra/
├── docker-compose.yml
├── mosquitto.conf
├── kubernetes/api-deployment.yaml
└── terraform/
```
