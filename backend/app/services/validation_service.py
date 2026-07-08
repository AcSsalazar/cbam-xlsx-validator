"""Apply dynamic and hand-coded validation rules to a records DataFrame.

For each row in ``records_df`` and each :class:`FieldSpec` describing a
column, this service:

1. Runs the dynamic ``required`` check when the field is mandatory.
2. Runs the dynamic ``max_length`` and ``digit_pattern`` checks when the
   :class:`FieldSpec` carries them.
3. Runs the dynamic ``allowed_values`` check against the ISO 3166-1 alpha-2
   list when ``is_iso_3166`` is set.
4. Runs the hand-coded rules from :mod:`app.validators.field_rules`.

Empty values short-circuit every check except ``required``: an empty value
is only a problem when the field is mandatory, and is otherwise ignored by
the remaining rules so optional fields do not produce noise.

The result is a tuple ``(valid_df, errors)`` where:

- ``valid_df`` contains only the rows that produced zero errors, with the
  original index preserved for traceability.
- ``errors`` is a list of :class:`app.schemas.upload.FieldError`, one per
  individual rule violation (so a single row can produce multiple errors).
"""
from __future__ import annotations

from typing import Any

import pandas as pd

from app.schemas.upload import FieldError
from app.schemas.workbook import FieldSpec
from app.validators import _registry
from app.validators.field_rules import FIELD_RULES, ISO_3166_ALPHA2


class ValidationService:
    """Apply the full set of rules to every cell of a records DataFrame."""

    def validate(
        self,
        records_df: pd.DataFrame,
        field_specs: list[FieldSpec],
    ) -> tuple[pd.DataFrame, list[FieldError]]:
        errors: list[FieldError] = []
        valid_indexes: list[int] = []

        for original_index, row in records_df.iterrows():
            row_number = self._row_number(original_index)
            row_errors: list[FieldError] = []

            for spec in field_specs:
                value = row.get(spec.name)
                row_errors.extend(self._validate_field(row_number, spec, value))

            if row_errors:
                errors.extend(row_errors)
            else:
                valid_indexes.append(original_index)

        valid_df = records_df.loc[valid_indexes]
        return valid_df, errors

    def _validate_field(
        self,
        row_number: int,
        spec: FieldSpec,
        value: Any,
    ) -> list[FieldError]:
        results: list[FieldError] = []
        is_blank = self._is_blank(value)

        if spec.required and is_blank:
            return [
                FieldError(
                    row=row_number,
                    field=spec.name,
                    value=value,
                    message="is required",
                )
            ]

        # For non-mandatory fields, an empty value skips every remaining check.
        if is_blank:
            return results

        # Dynamic rules derived from the Rules sheet.
        if spec.max_length is not None:
            results.extend(
                self._run(
                    row_number,
                    spec.name,
                    value,
                    "max_length",
                    {"max": spec.max_length},
                )
            )

        if spec.digit_pattern is not None:
            results.extend(
                self._run(
                    row_number,
                    spec.name,
                    value,
                    "regex",
                    {
                        "pattern": spec.digit_pattern,
                        "message": "Must contain only digits of the expected length",
                    },
                )
            )

        if spec.is_iso_3166:
            results.extend(
                self._run(
                    row_number,
                    spec.name,
                    value,
                    "allowed_values",
                    {
                        "values": ISO_3166_ALPHA2,
                        "message": "Must be a valid ISO 3166-1 alpha-2 country code",
                    },
                )
            )

        # Hand-coded rules from field_rules.py.
        for rule_name, params in FIELD_RULES.get(spec.name, []):
            results.extend(
                self._run(row_number, spec.name, value, rule_name, params)
            )

        return results

    def _run(
        self,
        row_number: int,
        field_name: str,
        value: Any,
        rule_name: str,
        params: dict,
    ) -> list[FieldError]:
        rule = _registry.get(rule_name)
        if rule is None:
            return []
        messages = rule(value, params)
        return [
            FieldError(
                row=row_number,
                field=field_name,
                value=value,
                message=message,
            )
            for message in messages
        ]

    @staticmethod
    def _is_blank(value: Any) -> bool:
        if value is None:
            return True
        if isinstance(value, float) and pd.isna(value):
            return True
        if isinstance(value, str) and value.strip() == "":
            return True
        return False

    @staticmethod
    def _row_number(original_index: int) -> int:
        # ``pd.DataFrame.iterrows`` yields the original index. The first data
        # row in the Excel file is row 2 (row 1 is the header), so we add 2.
        return int(original_index) + 2
