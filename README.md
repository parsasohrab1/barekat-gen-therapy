# Barekat Gen Therapy

پلتفرم end-to-end برای طراحی و بهینه‌سازی ناقل‌های لیپیدی ژن‌درمانی: تولید داده سنتتیک (CK4Gen)، پیش‌بینی بقا (CoxPH)، طراحی/رتبه‌بندی مولکول (RDKit)، یکپارچه‌سازی آزمایشگاه، جستجوی برداری (Qdrant)، و انطباق HIPAA/GDPR/GMP.

## راه‌اندازی سریع

```bash
cp .env.example .env
make up
make seed-users
make seed-invitro
```

| سرویس | آدرس |
|-------|------|
| Frontend | http://localhost:5173 |
| API / OpenAPI | http://localhost:8000/docs |
| MLflow | http://localhost:5000 |
| Qdrant | http://localhost:6333 |
| MinIO | http://localhost:9001 |
| MQTT | localhost:1883 |

## کاربران staging

| کاربر | رمز | نقش |
|-------|-----|-----|
| `scientist` | `scientist123` | طراحی، آزمایشگاه، پیش‌بینی تحقیقاتی |
| `clinician` | `clinician123` | پیش‌بینی بالینی |
| `admin` | `admin123` | انطباق، audit، حذف GDPR |
| `viewer` | `viewer123` | فقط خواندن |

## جریان محصول

1. **داده سنتتیک** — CK4Gen + اعتبارسنجی KS/C-index → آموزش CoxPH + MLflow
2. **پیش‌بینی پیامد** — CoxPH فعال + audit log
3. **طراحی لیپید** — فیلتر RDKit + dedupe Qdrant + رتبه‌بندی چندمعیاره
4. **آزمایشگاه** — LIMS sync → MQTT سنتز → import in-vitro → retrain
5. **انطباق** — pseudonymize، GDPR delete، GMP trace، Part 11 audit

## مستندات

- [API](docs/API.md)
- [استقرار](docs/DEPLOYMENT.md)
- [معماری](docs/ARCHITECTURE.md)

## توسعه

```bash
make install
make migrate
make test
make lint
```

نسخه فعلی: **1.0.0**
