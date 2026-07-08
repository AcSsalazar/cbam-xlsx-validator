"""Functional tests for ``GET /records``."""
from __future__ import annotations

from tests._xlsx_helpers import build_xlsx


def _valid_row() -> list:
    return [
        "DE123456789012345", "ArcelorMittal SA", "Address", "John Doe",
        "DEHSt", "CBAM-DE-2026-00142", "Sam Smith", "7207111400",
        "72071114", "Goods", "Iron and Steel", "Complex", "1250",
        "05.05.2026", "CN", "DE/2026/MRN-ABC-123456", "Supplier Ch1",
        "Notes",
    ]


def test_records_empty(client_with_db):
    response = client_with_db.get("/records")
    assert response.status_code == 200
    body = response.json()
    assert body == {"page": 1, "page_size": 20, "total": 0, "items": []}


def test_records_pagination_default(client_with_db):
    workbook_bytes = build_xlsx([_valid_row() for _ in range(3)])
    client_with_db.post(
        "/upload",
        files={"file": ("sample.xlsx", workbook_bytes, "application/octet-stream")},
    )
    response = client_with_db.get("/records")
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["page_size"] == 20
    assert body["total"] == 3
    assert len(body["items"]) == 3


def test_records_pagination_explicit(client_with_db):
    workbook_bytes = build_xlsx([_valid_row() for _ in range(5)])
    client_with_db.post(
        "/upload",
        files={"file": ("sample.xlsx", workbook_bytes, "application/octet-stream")},
    )

    page_1 = client_with_db.get("/records?page=1&page_size=2").json()
    page_2 = client_with_db.get("/records?page=2&page_size=2").json()
    page_3 = client_with_db.get("/records?page=3&page_size=2").json()

    assert page_1["total"] == page_2["total"] == page_3["total"] == 5
    assert len(page_1["items"]) == 2
    assert len(page_2["items"]) == 2
    assert len(page_3["items"]) == 1


def test_records_invalid_page_returns_422(client_with_db):
    response = client_with_db.get("/records?page=0")
    assert response.status_code == 422


def test_records_invalid_page_size_returns_422(client_with_db):
    response = client_with_db.get("/records?page_size=200")
    assert response.status_code == 422


def test_records_ordered_by_created_at_desc(client_with_db):
    workbook_bytes = build_xlsx([_valid_row() for _ in range(3)])
    client_with_db.post(
        "/upload",
        files={"file": ("sample.xlsx", workbook_bytes, "application/octet-stream")},
    )
    body = client_with_db.get("/records").json()
    timestamps = [item["created_at"] for item in body["items"]]
    assert timestamps == sorted(timestamps, reverse=True)
