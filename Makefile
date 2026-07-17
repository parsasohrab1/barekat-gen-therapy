.PHONY: help install dev up down logs migrate seed seed-users seed-invitro test lint ci

help:
	@echo "Barekat Gen Therapy — دستورات توسعه"
	@echo ""
	@echo "  make install       نصب وابستگی‌ها"
	@echo "  make up            استک Docker"
	@echo "  make down          توقف"
	@echo "  make migrate       alembic upgrade"
	@echo "  make seed          داده اولیه"
	@echo "  make seed-users    کاربران staging"
	@echo "  make seed-invitro  داده برون‌تنی دمو"
	@echo "  make test          pytest"
	@echo "  make lint          ruff"

install:
	cd backend && pip install -e ".[dev]"
	cd frontend && npm install

dev:
	cd backend && PYTHONPATH="$(CURDIR)/backend;$(CURDIR)/data" uvicorn app.main:app --reload --port 8000

up:
	cd infra && docker compose up --build -d

down:
	cd infra && docker compose down

logs:
	cd infra && docker compose logs -f

migrate:
	cd backend && alembic upgrade head

seed:
	python scripts/seed_db.py

seed-users:
	python scripts/seed_users.py

seed-invitro:
	python scripts/seed_invitro.py

test:
	cd backend && pytest -v

lint:
	cd backend && ruff check .

ci: lint test
