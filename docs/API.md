# API Reference

Base: `/api/v1` — OpenAPI interactive: `/docs`

Auth: `Authorization: Bearer <jwt>` وقتی `AUTH_ENABLED=true`.

## Auth

| Method | Path | نقش | توضیح |
|--------|------|-----|-------|
| POST | `/auth/login` | — | دریافت JWT |
| GET | `/auth/me` | authenticated | کاربر فعلی |

## Synthetic

| Method | Path | نقش | توضیح |
|--------|------|-----|-------|
| POST | `/synthetic/generate` | scientist | شروع job تولید CK4Gen |
| GET | `/synthetic/jobs/{id}` | viewer | وضعیت / نتیجه job |

Body نمونه:

```json
{ "n_patients": 300, "n_genes": 25, "seed": 42, "use_ck4gen": true, "n_clusters": 5 }
```

## Design

| Method | Path | نقش | توضیح |
|--------|------|-----|-------|
| POST | `/design/jobs` | scientist | شروع job طراحی لیپید |
| GET | `/design/jobs/{id}` | viewer | وضعیت job |
| POST | `/design/jobs/{id}/rank` | scientist | رتبه‌بندی چندمعیاره |

## Predict

| Method | Path | نقش | توضیح |
|--------|------|-----|-------|
| POST | `/predict/outcome` | clinician (+ scientist) | پیش‌بینی CoxPH با audit |

## Jobs / Models

| Method | Path | نقش | توضیح |
|--------|------|-----|-------|
| GET | `/jobs` | viewer | لیست jobها (`?job_type=`) |
| GET | `/models` | viewer | نسخه‌های مدل |
| GET | `/models/active` | viewer | مدل فعال |

## Lab Integration

| Method | Path | نقش | توضیح |
|--------|------|-----|-------|
| POST | `/lab/lims/sync` | scientist | Sync از LIMS (یا mock) |
| GET | `/lab/lims/mock` | — | فید دمو LIMS |
| POST | `/lab/synthesis/dispatch` | scientist | MQTT به ربات سنتز |
| POST | `/lab/invitro/import` | scientist | Import نتایج برون‌تنی |
| POST | `/lab/retrain` | scientist | Retrain از داده واقعی |

## Molecular Search (Qdrant)

| Method | Path | نقش | توضیح |
|--------|------|-----|-------|
| POST | `/molecules/index` | scientist | Index SMILES |
| POST | `/molecules/search` | viewer | جستجوی مشابه |
| POST | `/molecules/deduplicate` | scientist | تشخیص تکراری |
| POST | `/molecules/seed-library` | scientist | Index لیپیدهای seed |

## Compliance

| Method | Path | نقش | توضیح |
|--------|------|-----|-------|
| POST | `/compliance/patients/pseudonymize` | admin | HIPAA/GDPR |
| DELETE | `/compliance/patients/{id}` | admin | GDPR erasure |
| POST | `/compliance/gmp/record` | scientist | ثبت مرحله GMP |
| GET | `/compliance/gmp/trace/{batch_id}` | viewer | ردیابی batch |
| GET | `/compliance/audit` | admin | 21 CFR Part 11 |

## Health & Observability

| Method | Path | توضیح |
|--------|------|-------|
| GET | `/health` | database / redis / qdrant |
| GET | `/metrics` | Prometheus |
