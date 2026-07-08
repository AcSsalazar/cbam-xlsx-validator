import os

# Must be set before any app.* import so that the SQLAlchemy engine created
# at module-load time in app.database.session binds to the in-memory test DB.
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")

import pytest
from app.database.base import Base
from app.database.session import get_db
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tests._xlsx_helpers import build_xlsx

TEST_DATABASE_URL = os.environ["DATABASE_URL"]


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


@pytest.fixture
def db_session(test_engine, test_session_local):
    Base.metadata.create_all(test_engine)
    session = test_session_local()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(test_engine)


@pytest.fixture
def client_with_db(tmp_path):
    """A TestClient backed by a fresh file-based SQLite database per test.

    File-based (not in-memory) so the test engine and the FastAPI app
    engine see the same database. The file is removed after the test.
    """
    db_file = tmp_path / "functional_test.db"
    db_url = f"sqlite+pysqlite:///{db_file.as_posix()}"

    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
        db_file.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Sample workbook fixtures
# ---------------------------------------------------------------------------

_VALID_ROW = [
    "DE123456789012345",
    "ArcelorMittal SA",
    "24-26 Boulevard d'Avranches, L-1160 Luxembourg",
    "John Doe, john.doe@company.com",
    "DEHSt",
    "CBAM-DE-2026-00142",
    "Sam Smith, sam.smith@company.com",
    "7207111400",
    "72071114",
    "Semi-finished iron or non-alloy steel",
    "Iron and Steel",
    "Complex",
    "1250",
    "05.05.2026",
    "CN",
    "DE/2026/MRN-ABC-123456",
    "Supplier Ch1",
    "MRV plan is under preparation",
]


@pytest.fixture
def sample_xlsx_bytes() -> bytes:
    """A workbook with 1 valid row + 4 invalid rows for functional tests."""
    return build_xlsx(
        template_rows=[
            _VALID_ROW,
            # Row 2: EORI Number missing (mandatory).
            [
                "", "ArcelorMittal SA", "Address", "John Doe", "DEHSt",
                "CBAM-DE-2026-00142", "Sam Smith", "7207111400", "72071114",
                "Goods", "Iron and Steel", "Complex", "1250", "05.05.2026",
                "CN", "DE/2026/MRN-ABC-123456", "Supplier Ch1", "Notes",
            ],
            # Row 3: TARIC Code wrong format; CN Code wrong format.
            [
                "DE123456789012345", "ArcelorMittal SA", "Address", "John Doe",
                "DEHSt", "CBAM-DE-2026-00142", "Sam Smith",
                "ABC123", "1234",
                "Goods", "Iron and Steel", "Complex", "1250", "05.05.2026",
                "CN", "DE/2026/MRN-ABC-123456", "Supplier Ch1", "Notes",
            ],
            # Row 4: Import Volume negative; Product Type out of allowed values.
            [
                "DE123456789012345", "ArcelorMittal SA", "Address", "John Doe",
                "DEHSt", "CBAM-DE-2026-00142", "Sam Smith", "7207111400",
                "72071114", "Goods", "Iron and Steel",
                "Unknown", "-50",
                "05.05.2026", "CN", "DE/2026/MRN-ABC-123456", "Supplier Ch1",
                "Notes",
            ],
            # Row 5: Date of importation wrong format; Country not ISO 3166-1.
            [
                "DE123456789012345", "ArcelorMittal SA", "Address", "John Doe",
                "DEHSt", "CBAM-DE-2026-00142", "Sam Smith", "7207111400",
                "72071114", "Goods", "Iron and Steel", "Complex", "1250",
                "2026-05-05", "XX",
                "DE/2026/MRN-ABC-123456", "Supplier Ch1", "Notes",
            ],
        ]
    )


@pytest.fixture
def sample_xlsx_bytes_sheet1() -> bytes:
    """Same as ``sample_xlsx_bytes`` but the rules sheet is named ``Sheet1``."""
    return build_xlsx(
        template_rows=[_VALID_ROW],
        rules_sheet_name="Sheet1",
    )
