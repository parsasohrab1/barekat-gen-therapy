# API Reference

Base: `/api/v1` — OpenAPI interactive: `/docs`

Auth: `Authorization: Bearer <jwt>` when `AUTH_ENABLED=true`.

## Auth

| Method | Path | Role | Description |
|--------|------|-----|-------|
| POST | `/auth/login` | — | Obtain JWT |
| GET | `/auth/me` | authenticated | Current user |

## Synthetic

| Method | Path | Role | Description |
|--------|------|-----|-------|
| POST | `/synthetic/generate` | scientist | Start a CK4Gen generation job |
| GET | `/synthetic/jobs/{id}` | viewer | Job status / result |

Sample body:

```json
{ "n_patients": 300, "n_genes": 25, "seed": 42, "use_ck4gen": true, "n_clusters": 5 }
```

## Design

| Method | Path | Role | Description |
|--------|------|-----|-------|
| POST | `/design/jobs` | scientist | Start a lipid design job |
| GET | `/design/jobs/{id}` | viewer | Job status |
| POST | `/design/jobs/{id}/rank` | scientist | Multi-criteria ranking |

## Predict

| Method | Path | Role | Description |
|--------|------|-----|-------|
| POST | `/predict/outcome` | clinician (+ scientist) | CoxPH prediction with audit |

## Jobs / Models

| Method | Path | Role | Description |
|--------|------|-----|-------|
| GET | `/jobs` | viewer | List jobs (`?job_type=`) |
| GET | `/models` | viewer | Model versions |
| GET | `/models/active` | viewer | Active model |

## Lab Integration

| Method | Path | Role | Description |
|--------|------|-----|-------|
| POST | `/lab/lims/sync` | scientist | Sync from LIMS (or mock) |
| GET | `/lab/lims/mock` | — | LIMS demo feed |
| POST | `/lab/synthesis/dispatch` | scientist | MQTT to the synthesis robot |
| POST | `/lab/invitro/import` | scientist | Import in-vitro results |
| POST | `/lab/retrain` | scientist | Retrain from real data |

## Molecular Search (Qdrant)

| Method | Path | Role | Description |
|--------|------|-----|-------|
| POST | `/molecules/index` | scientist | Index SMILES |
| POST | `/molecules/search` | viewer | Similarity search |
| POST | `/molecules/deduplicate` | scientist | Duplicate detection |
| POST | `/molecules/seed-library` | scientist | Index seed lipids |

## Compliance

| Method | Path | Role | Description |
|--------|------|-----|-------|
| POST | `/compliance/patients/pseudonymize` | admin | HIPAA/GDPR |
| DELETE | `/compliance/patients/{id}` | admin | GDPR erasure |
| POST | `/compliance/gmp/record` | scientist | Record a GMP step |
| GET | `/compliance/gmp/trace/{batch_id}` | viewer | Batch tracing |
| GET | `/compliance/audit` | admin | 21 CFR Part 11 |

## Health & Observability

| Method | Path | Description |
|--------|------|-------|
| GET | `/health` | database / redis / qdrant |
| GET | `/metrics` | Prometheus |
