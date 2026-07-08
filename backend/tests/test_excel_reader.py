"""Unit tests for :class:`app.services.excel_reader.ExcelReader`."""
from __future__ import annotations

from io import BytesIO

import openpyxl
import pytest

from app.core.exceptions import AppException
from app.services.excel_reader import ExcelReader


def _build_xlsx(sheets: dict[str, list[list]]) -> bytes:
    """Build a minimal .xlsx in memory. ``sheets`` maps sheet name to rows."""
    workbook = openpyxl.Workbook()
    # Remove the default sheet; we'll add our own.
    default = workbook.active
    workbook.remove(default)
    for name, rows in sheets.items():
        sheet = workbook.create_sheet(title=name)
        for row in rows:
            sheet.append(row)
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


@pytest.fixture
def reader() -> ExcelReader:
    return ExcelReader()


def test_read_happy_path_with_rules_sheet(reader):
    content = _build_xlsx(
        {
            "Template": [["EORI Number", "CN Code"], ["DE1", "72071114"]],
            "Rules": [
                [
                    "Field",
                    "Purpose",
                    "Mandatory/optional for compliance",
                    "Mandatory/optional for impact assessment",
                    "Data type/format",
                ],
                ["EORI Number", "...", "Mandatory", "No", "Text (up to 17 chars)"],
                ["CN Code", "...", "Mandatory", "Yes", "Numeric (8 digits)"],
            ],
        }
    )
    records_df, rules_df = reader.read(content)
    assert list(records_df.columns) == ["EORI Number", "CN Code"]
    assert len(records_df) == 1
    assert list(rules_df["Field"]) == ["EORI Number", "CN Code"]


def test_read_accepts_sheet1_as_rules_sheet(reader):
    content = _build_xlsx(
        {
            "Template": [["EORI Number"], ["DE1"]],
            "Sheet1": [
                [
                    "Field",
                    "Purpose",
                    "Mandatory/optional for compliance",
                    "Mandatory/optional for impact assessment",
                    "Data type/format",
                ],
                ["EORI Number", "...", "Mandatory", "No", "Text"],
            ],
        }
    )
    records_df, rules_df = reader.read(content)
    assert len(records_df) == 1
    assert "Field" in rules_df.columns


def test_missing_template_sheet_raises(reader):
    content = _build_xlsx(
        {
            "Rules": [
                [
                    "Field",
                    "Purpose",
                    "Mandatory/optional for compliance",
                    "Mandatory/optional for impact assessment",
                    "Data type/format",
                ],
                ["EORI Number", "...", "Mandatory", "No", "Text"],
            ]
        }
    )
    with pytest.raises(AppException) as exc:
        reader.read(content)
    assert exc.value.status_code == 400
    assert "Template" in exc.value.message


def test_missing_rules_sheet_raises(reader):
    content = _build_xlsx({"Template": [["EORI Number"]]})
    with pytest.raises(AppException) as exc:
        reader.read(content)
    assert exc.value.status_code == 400
    assert "rules sheet" in exc.value.message.lower()


def test_invalid_xlsx_raises(reader):
    with pytest.raises(AppException) as exc:
        reader.read(b"this is not an xlsx file")
    assert exc.value.status_code == 400


def test_values_kept_as_strings_no_silent_coercion(reader):
    """A value that looks like a date in the source must not become an int."""
    content = _build_xlsx(
        {
            "Template": [["Date of importation"], ["05.05.2026"]],
            "Rules": [
                [
                    "Field",
                    "Purpose",
                    "Mandatory/optional for compliance",
                    "Mandatory/optional for impact assessment",
                    "Data type/format",
                ],
                ["Date of importation", "...", "Mandatory", "Yes", "Integer"],
            ],
        }
    )
    records_df, _ = reader.read(content)
    assert records_df["Date of importation"].iloc[0] == "05.05.2026"
