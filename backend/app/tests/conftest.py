import os

import pytest
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

TEST_DATABASE_URL = "sqlite+pysqlite:///:memory:"


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    return engine


@pytest.fixture(scope="session")
def test_session_local(test_engine):
    return sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="session")
def client():
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    with TestClient(app) as test_client:
        yield test_client
