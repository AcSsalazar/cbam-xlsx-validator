from sqlalchemy.orm import Session

from app.models.import_job import ImportJob


class ImportJobRepository:
    """Persistence gateway for ImportJob aggregates."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        filename: str,
        total_rows: int,
        valid_rows: int,
        invalid_rows: int,
    ) -> ImportJob:
        job = ImportJob(
            filename=filename,
            total_rows=total_rows,
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get(self, import_job_id: int) -> ImportJob | None:
        return self.db.get(ImportJob, import_job_id)
