"""Orchestrate a complete Excel import.

This service wires together every other piece of the import pipeline and
contains no validation or business logic of its own. Its only job is to
call each component in the right order and persist the result.

Pipeline:

    ExcelReader.read()
      -> RulesReader.parse()
      -> WorkbookValidator.validate()
      -> ValidationService.validate()
      -> ImportJobRepository.create()
      -> RecordRepository.create_many()  (valid rows only)
      -> UploadReport
"""
from __future__ import annotations

import pandas as pd
from sqlalchemy.orm import Session

from app.repositories.import_job_repository import ImportJobRepository
from app.repositories.record_repository import RecordRepository
from app.schemas.upload import UploadReport
from app.services.excel_reader import ExcelReader
from app.services.rules_reader import RulesReader
from app.services.validation_service import ValidationService
from app.services.workbook_validator import WorkbookValidator


class ImportService:
    """Coordinate the Excel ingestion pipeline."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.reader = ExcelReader()
        self.rules_reader = RulesReader()
        self.workbook_validator = WorkbookValidator()
        self.validator = ValidationService()
        self.jobs = ImportJobRepository(db)
        self.records = RecordRepository(db)

    def import_file(self, content: bytes, filename: str) -> UploadReport:
        records_df, rules_df = self.reader.read(content)
        specs = self.rules_reader.parse(rules_df)
        self.workbook_validator.validate(records_df, specs)

        total_rows = len(records_df)
        if total_rows == 0:
            raise AppException(
                "The uploaded file contains no data rows. "
                "Please fill in the Template sheet and try again.",
                status_code=400,
            )
        valid_df, errors = self.validator.validate(records_df, specs)
        invalid_rows = len({error.row for error in errors})
        valid_rows = total_rows - invalid_rows

        job = self.jobs.create(
            filename=filename,
            total_rows=total_rows,
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
        )

        self.records.create_many(
            [
                {
                    "import_job_id": job.id,
                    "row_number": int(original_index) + 2,
                    "payload": self._payload(row),
                }
                for original_index, row in valid_df.iterrows()
            ]
        )

        return UploadReport(
            filename=filename,
            total_rows=total_rows,
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            errors=errors,
        )

    @staticmethod
    def _payload(row: pd.Series) -> dict:
        return {
            key: (None if pd.isna(value) else value)
            for key, value in row.to_dict().items()
        }
