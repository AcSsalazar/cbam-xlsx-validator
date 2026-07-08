"""Structural validation of an uploaded Excel workbook.

The validator enforces the contract between the Template sheet (the data
the user filled in) and the Rules sheet (the field declarations). It does
not validate individual cell values - that is the responsibility of
:class:`app.services.validation_service.ValidationService`.

Two checks are performed:

1. The set of column names in the Template sheet must match the set of
   field names declared in the Rules sheet.
2. The order in which they appear is *not* enforced - only set equality.

A mismatch in either direction raises :class:`app.core.exceptions.AppException`
with status code 400 and a descriptive message.
"""
from __future__ import annotations

import pandas as pd

from app.core.exceptions import AppException
from app.schemas.workbook import FieldSpec


class WorkbookValidator:
    """Ensure structural consistency between Template and Rules sheets."""

    def validate(
        self,
        records_df: pd.DataFrame,
        field_specs: list[FieldSpec],
    ) -> None:
        record_columns = set(records_df.columns)
        rule_fields = {spec.name for spec in field_specs}

        extra_in_template = sorted(record_columns - rule_fields)
        if extra_in_template:
            raise AppException(
                "Template sheet contains columns not declared in the Rules "
                f"sheet: {extra_in_template}",
                status_code=400,
            )

        missing_from_template = sorted(rule_fields - record_columns)
        if missing_from_template:
            raise AppException(
                "Rules sheet declares fields missing from the Template "
                f"sheet: {missing_from_template}",
                status_code=400,
            )
