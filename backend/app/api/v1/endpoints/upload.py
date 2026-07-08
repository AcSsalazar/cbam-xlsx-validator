"""Endpoint to upload a CBAM .xlsx file and ingest its records."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.database.session import get_db
from app.schemas.upload import UploadReport
from app.services.import_service import ImportService

router = APIRouter()

MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/upload", response_model=UploadReport)
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> UploadReport:
    if not (file.filename or "").lower().endswith(".xlsx"):
        raise AppException(
            "Only .xlsx files are accepted",
            status_code=400,
        )
    content = file.file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise AppException(
            f"File too large. Maximum size is 10 MB, got {len(content) / (1024 * 1024):.2f} MB",
            status_code=400,
        )
    return ImportService(db).import_file(content, file.filename)
