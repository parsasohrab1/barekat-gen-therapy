import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


@pytest.fixture(autouse=True)
def test_settings(monkeypatch):
    os.environ["AUTH_ENABLED"] = "false"
    os.environ["MLFLOW_ENABLED"] = "false"
    os.environ["QDRANT_ENABLED"] = "false"
    os.environ["MQTT_ENABLED"] = "false"
    os.environ["LIMS_ENABLED"] = "false"
    from app.core.config import settings

    monkeypatch.setattr(settings, "AUTH_ENABLED", False)
    monkeypatch.setattr(settings, "MLFLOW_ENABLED", False)
    monkeypatch.setattr(settings, "QDRANT_ENABLED", False)
    monkeypatch.setattr(settings, "MQTT_ENABLED", False)
    monkeypatch.setattr(settings, "LIMS_ENABLED", False)


@pytest.fixture
def db_session():
    """PostgreSQL session with rollback — skips when DB is unreachable."""
    try:
        import psycopg  # noqa: F401
    except ImportError:
        pytest.skip("psycopg not installed")

    from app.core.config import settings

    try:
        engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        pytest.skip(f"PostgreSQL unavailable: {exc}")

    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
        engine.dispose()
