from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RecordOut(BaseModel):
    """API representation of a single valid row persisted in the database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    import_job_id: int
    row_number: int
    payload: dict
    created_at: datetime


class PaginatedRecords(BaseModel):
    """Paginated wrapper around a list of RecordOut."""

    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1)
    total: int = Field(..., ge=0)
    items: list[RecordOut] = Field(default_factory=list)
