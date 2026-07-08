"""End-to-end integration test against the real CBAM template.

Exercises the full pipeline that the production code path will follow:

    ExcelReader.read()
      -> RulesReader.parse()
      -> WorkbookValidator.validate()
      -> ValidationService.validate()

The shipped template is the unfilled form: it has 18 column headers in
the Template sheet and 22 visually-empty rows beneath them. pandas drops
fully-empty rows on read, so the records DataFrame ends up with 0 rows.
The Rules sheet still parses into 18 FieldSpec objects, and the pipeline
runs cleanly on the empty records.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from app.services.excel_reader import ExcelReader
from app.services.rules_reader import RulesReader
from app.services.validation_service import ValidationService
from app.services.workbook_validator import WorkbookValidator

TEMPLATE_PATH = (
    Path(__file__).resolve().parents[1] / "tests" / "data" / "cbam_template.xlsx"
)


@pytest.fixture
def template_bytes() -> bytes:
    return TEMPLATE_PATH.read_bytes()


def test_real_template_end_to_end(template_bytes):
    records_df, rules_df = ExcelReader().read(template_bytes)
    assert "EORI Number" in records_df.columns
    assert "Notes / Comments" in records_df.columns
    # The shipped template is empty; pandas drops the 22 unfilled rows.
    assert len(records_df) == 0

    specs = RulesReader().parse(rules_df)
    assert len(specs) == 18
    assert {s.name for s in specs} == set(records_df.columns)

    # The shipped template marks 15 fields as mandatory and 3 as optional
    # (TARIC Code, Customs Declaration Ref, Notes / Comments).
    required = [s for s in specs if s.required]
    optional = [s for s in specs if not s.required]
    assert len(required) == 15
    assert {s.name for s in optional} == {
        "TARIC Code",
        "Customs Declaration Ref",
        "Notes / Comments",
    }

    WorkbookValidator().validate(records_df, specs)  # should not raise

    valid_df, errors = ValidationService().validate(records_df, specs)
    assert len(valid_df) == 0
    assert errors == []


def test_real_template_field_specs_match_actual_data(template_bytes):
    """Cross-check that the parsed FieldSpec captures the rules in the real file."""
    _records_df, rules_df = ExcelReader().read(template_bytes)
    specs = {s.name: s for s in RulesReader().parse(rules_df)}

    assert specs["EORI Number"].required is True
    assert specs["EORI Number"].max_length == 17

    assert specs["CN Code"].required is True
    assert specs["CN Code"].digit_pattern == r"^\d{8}$"

    assert specs["TARIC Code"].required is False  # Optional in both columns
    assert specs["TARIC Code"].digit_pattern == r"^\d{10}$"

    assert specs["Country of Origin"].required is True
    assert specs["Country of Origin"].is_iso_3166 is True

    assert specs["Product Type"].required is True
    assert specs["Product Type"].is_enum is True

    assert specs["Notes / Comments"].required is False

