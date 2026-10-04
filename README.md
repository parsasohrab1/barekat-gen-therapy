# Barekat Gen Therapy

End-to-end platform for designing and optimizing lipid vectors for gene therapy: synthetic data generation (CK4Gen), survival prediction (CoxPH), molecule design/ranking (RDKit), laboratory integration, vector search (Qdrant), and HIPAA/GDPR/GMP compliance.

## Quick Start

```bash
cp .env.example .env
make up
make seed-users
make seed-invitro
```

| Service | Address |
|-------|------|
| Frontend | http://localhost:5173 |
| API / OpenAPI | http://localhost:8000/docs |
| MLflow | http://localhost:5000 |
| Qdrant | http://localhost:6333 |
| MinIO | http://localhost:9001 |
| MQTT | localhost:1883 |

## Staging Users

| User | Password | Role |
|-------|-----|-----|
| `scientist` | `scientist123` | Design, laboratory, research prediction |
| `clinician` | `clinician123` | Clinical prediction |
| `admin` | `admin123` | Compliance, audit, GDPR deletion |
| `viewer` | `viewer123` | Read-only |

## Product Flow

1. **Synthetic data** — CK4Gen + KS/C-index validation → CoxPH training + MLflow
2. **Outcome prediction** — active CoxPH + audit log
3. **Lipid design** — RDKit filter + Qdrant dedupe + multi-criteria ranking
4. **Laboratory** — LIMS sync → MQTT synthesis → in-vitro import → retrain
5. **Compliance** — pseudonymize, GDPR delete, GMP trace, Part 11 audit

## Documentation

- [API](docs/API.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Architecture](docs/ARCHITECTURE.md)

## Development

```bash
make install
make migrate
make test
make lint
```

Current version: **1.0.0**
