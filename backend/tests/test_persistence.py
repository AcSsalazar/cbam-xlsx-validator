"""Smoke tests for the persistence layer introduced in iteration 1.

These tests intentionally avoid exercising business logic (upload, validation,
business rules) and focus on the four explicit verification targets:

1. The application starts and exposes /health.
2. The SQLAlchemy models can be created against SQLite.
3. The JSON column on Record round-trips through SQLite.
4. The first Alembic migration upgrades cleanly against SQLite.
"""
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.database.base import Base
from app.models.import_job import ImportJob
from app.models.record import Record


def test_app_starts(client):
    """The FastAPI app boots without import errors and /health returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_models_can_be_created(test_engine):
    """Base.metadata.create_all creates both tables against SQLite."""
    Base.metadata.create_all(test_engine)
    try:
        inspector = inspect(test_engine)
        table_names = set(inspector.get_table_names())
        assert "import_jobs" in table_names
        assert "records" in table_names
    finally:
        Base.metadata.drop_all(test_engine)


def test_record_persists_json_payload(db_session):
    """SQLite stores and returns the JSON payload unchanged."""
    job = ImportJob(
        filename="sample.xlsx",
        total_rows=1,
        valid_rows=1,
        invalid_rows=0,
    )
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)

    payload = {"a": 1, "b": [1, 2, 3], "c": "hello", "d": None, "e": {"nested": True}}
    record = Record(import_job_id=job.id, row_number=1, payload=payload)
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)

    assert record.id is not None
    assert record.payload == payload
    assert record.import_job_id == job.id


def test_alembic_upgrade_against_sqlite(tmp_path, monkeypatch):
    """The first Alembic migration runs cleanly against a fresh SQLite database."""
    from app.core.settings import get_settings

    db_file = tmp_path / "alembic_test.db"
    db_url = f"sqlite+pysqlite:///{db_file.as_posix()}"

    # alembic/env.py overrides sqlalchemy.url from Settings, so the test must
    # also override DATABASE_URL and clear the lru_cache so Settings re-reads it.
    monkeypatch.setenv("DATABASE_URL", db_url)
    get_settings.cache_clear()

    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    command.upgrade(config, "head")

    from sqlalchemy import create_engine

    file_engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
    )
    file_inspector = inspect(file_engine)
    try:
        table_names = set(file_inspector.get_table_names())
        assert "import_jobs" in table_names
        assert "records" in table_names

        import_jobs_indexes = {
            ix["name"] for ix in file_inspector.get_indexes("import_jobs")
        }
        records_indexes = {
            ix["name"] for ix in file_inspector.get_indexes("records")
        }
        assert "ix_import_jobs_uploaded_at" in import_jobs_indexes
        assert "ix_records_import_job_id" in records_indexes
    finally:
        file_engine.dispose()
        db_file.unlink(missing_ok=True)
