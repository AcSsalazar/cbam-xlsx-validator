"""Endpoint to list persisted records, paginated."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.repositories.record_repository import RecordRepository
from app.schemas.record import PaginatedRecords, RecordOut

router = APIRouter()


@router.get("/records", response_model=PaginatedRecords)
def list_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedRecords:
    repo = RecordRepository(db)
    total = repo.count()
    items = repo.list_paginated(
        limit=page_size,
        offset=(page - 1) * page_size,
    )
    return PaginatedRecords(
        page=page,
        page_size=page_size,
        total=total,
        items=[RecordOut.model_validate(record) for record in items],
    )
