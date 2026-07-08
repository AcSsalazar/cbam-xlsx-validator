"""Internal workbook schema.

This dataclass is constructed by :class:`app.services.rules_reader.RulesReader`
from the Rules sheet of the uploaded Excel file. It is consumed by
:class:`app.services.workbook_validator.WorkbookValidator` and
:class:`app.services.validation_service.ValidationService`.

It is intentionally a plain dataclass and not a Pydantic model: it never
crosses the HTTP boundary and is built from already-validated in-memory data.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FieldSpec:
    """A field declaration derived from the Rules sheet of the Excel file."""

    name: str
    required: bool
    max_length: int | None = None
    digit_pattern: str | None = None
    is_enum: bool = False
    is_iso_3166: bool = False
