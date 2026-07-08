"""Parse the Rules sheet of a CBAM intake workbook into ``FieldSpec`` objects.

The Rules sheet has a fixed shape:

- Column 1: ``Field`` (the field name as it appears in the Template sheet).
- Column 3: ``Mandatory/optional for compliance`` (note the trailing space
  in the source file - values are stripped before comparison).
- Column 4: ``Mandatory/optional for impact assessment``.
- Column 5: ``Data type/format``.

A field is **required** when column 3 equals ``"Mandatory"`` *or* column 4
equals ``"Yes"`` (after stripping whitespace).

The data-type column is parsed for these patterns:

- ``Text (up to N chars)`` -> ``max_length = N``
- ``Text (N digits)`` or ``Numeric (N digits)`` -> ``digit_pattern = r"^\\d{N}$"``
- ``Enum`` -> ``is_enum = True``
- ``ISO 3166-1`` -> ``is_iso_3166 = True``

All other values in column 5 leave the corresponding attributes as their
defaults.
"""
from __future__ import annotations

import re
from typing import ClassVar

import pandas as pd

from app.core.exceptions import AppException
from app.schemas.workbook import FieldSpec

_MAX_LENGTH_RE = re.compile(r"up to (\d+) chars", re.IGNORECASE)
_DIGITS_RE = re.compile(r"\b(\d+)\s*digits\b", re.IGNORECASE)


class RulesReader:
    """Build :class:`FieldSpec` objects from a Rules-sheet DataFrame."""

    # Exact column names as they appear in the source Excel file.
    COL_FIELD: ClassVar[str] = "Field"
    COL_MANDATORY_COMPLIANCE: ClassVar[str] = "Mandatory/optional for compliance"
    COL_MANDATORY_IMPACT: ClassVar[str] = "Mandatory/optional for impact assessment"
    COL_DATA_TYPE: ClassVar[str] = "Data type/format"

    REQUIRED_COMPLIANCE: ClassVar[str] = "Mandatory"
    REQUIRED_IMPACT: ClassVar[str] = "Yes"

    def parse(self, rules_df: pd.DataFrame) -> list[FieldSpec]:
        """Return one :class:`FieldSpec` per row of the Rules sheet."""
        self._ensure_columns(rules_df)

        specs: list[FieldSpec] = []
        for _, row in rules_df.iterrows():
            name = self._read_str(row, self.COL_FIELD)
            if not name:
                # Skip fully empty rows defensively; the workbook validator
                # will catch any structural issue at a higher level.
                continue
            specs.append(
                FieldSpec(
                    name=name,
                    required=self._is_required(row),
                    max_length=self._parse_max_length(row),
                    digit_pattern=self._parse_digit_pattern(row),
                    is_enum=self._parse_is_enum(row),
                    is_iso_3166=self._parse_is_iso_3166(row),
                )
            )
        return specs

    def _ensure_columns(self, rules_df: pd.DataFrame) -> None:
        required_cols = {
            self.COL_FIELD,
            self.COL_MANDATORY_COMPLIANCE,
            self.COL_MANDATORY_IMPACT,
            self.COL_DATA_TYPE,
        }
        missing = required_cols - set(rules_df.columns)
        if missing:
            raise AppException(
                f"Rules sheet is missing required columns: {sorted(missing)}",
                status_code=400,
            )

    @staticmethod
    def _read_str(row: pd.Series, col: str) -> str:
        value = row.get(col)
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return ""
        return str(value).strip()

    def _is_required(self, row: pd.Series) -> bool:
        compliance = self._read_str(row, self.COL_MANDATORY_COMPLIANCE)
        impact = self._read_str(row, self.COL_MANDATORY_IMPACT)
        return (
            compliance == self.REQUIRED_COMPLIANCE
            or impact == self.REQUIRED_IMPACT
        )

    def _parse_max_length(self, row: pd.Series) -> int | None:
        data_type = self._read_str(row, self.COL_DATA_TYPE)
        match = _MAX_LENGTH_RE.search(data_type)
        if match is None:
            return None
        return int(match.group(1))

    def _parse_digit_pattern(self, row: pd.Series) -> str | None:
        data_type = self._read_str(row, self.COL_DATA_TYPE).lower()
        if "digit" not in data_type:
            return None
        match = _DIGITS_RE.search(data_type)
        if match is None:
            return None
        n = int(match.group(1))
        return rf"^\d{{{n}}}$"

    @staticmethod
    def _parse_is_enum(row: pd.Series) -> bool:
        data_type = RulesReader._read_str(row, RulesReader.COL_DATA_TYPE)
        return data_type.strip().lower() == "enum"

    @staticmethod
    def _parse_is_iso_3166(row: pd.Series) -> bool:
        data_type = RulesReader._read_str(row, RulesReader.COL_DATA_TYPE)
        return "iso 3166" in data_type.lower()
