from typing import Any

from pydantic import BaseModel, Field


class FieldError(BaseModel):
    """A single field-level validation error tied to a row in the Excel file."""

    row: int = Field(..., ge=1, description="1-indexed row number in the source sheet.")
    field: str = Field(..., min_length=1, description="Column name where the error occurred.")
    value: Any = Field(..., description="The value that was received for that field.")
    message: str = Field(..., min_length=1, description="Human-readable error message.")


class UploadReport(BaseModel):
    """Summary of a single Excel upload, including the per-row error list."""

    filename: str
    total_rows: int = Field(..., ge=0)
    valid_rows: int = Field(..., ge=0)
    invalid_rows: int = Field(..., ge=0)
    errors: list[FieldError] = Field(default_factory=list)
