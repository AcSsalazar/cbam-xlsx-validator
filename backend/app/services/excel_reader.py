"""Low-level reader for a CBAM intake Excel file.

The reader is intentionally a pure I/O component: it opens the workbook,
locates the two required sheets, and returns their content as pandas
DataFrames. It performs no validation of the content - that is the job of
:class:`app.services.workbook_validator.WorkbookValidator` and
:class:`app.services.validation_service.ValidationService`.

The Template sheet is loaded with ``dtype=str`` so that pandas does not
silently coerce values like ``05.05.2026`` into integers.
"""
from __future__ import annotations

import io

import pandas as pd

from app.core.exceptions import AppException

TEMPLATE_SHEET = "Template"
RULES_SHEET_CANDIDATES: tuple[str, ...] = ("Rules", "Sheet1")


class ExcelReader:
    """Read the Template and Rules sheets from a CBAM .xlsx file."""

    def read(self, content: bytes) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Return ``(records_df, rules_df)``.

        Raises :class:`AppException` with status 400 if:

        - The file cannot be parsed as an .xlsx.
        - The Template sheet is missing.
        - No sheet named either ``Rules`` or ``Sheet1`` is present.
        """
        try:
            xls = pd.ExcelFile(io.BytesIO(content))
        except Exception as exc:
            raise AppException(
                f"Invalid .xlsx file: {exc}",
                status_code=400,
            ) from exc

        sheet_names = set(xls.sheet_names)

        if TEMPLATE_SHEET not in sheet_names:
            raise AppException(
                f"Missing required sheet: {TEMPLATE_SHEET!r}",
                status_code=400,
            )

        rules_sheet = next(
            (name for name in RULES_SHEET_CANDIDATES if name in sheet_names),
            None,
        )
        if rules_sheet is None:
            raise AppException(
                "Missing rules sheet. Expected one of: "
                f"{list(RULES_SHEET_CANDIDATES)}",
                status_code=400,
            )

        records_df = pd.read_excel(
            xls,
            sheet_name=TEMPLATE_SHEET,
            dtype=str,
            keep_default_na=False,
        )
        rules_df = pd.read_excel(
            xls,
            sheet_name=rules_sheet,
            dtype=str,
            keep_default_na=False,
        )
        return records_df, rules_df
