"""Unit tests for :class:`app.services.rules_reader.RulesReader`."""
from __future__ import annotations

import pandas as pd
import pytest

from app.core.exceptions import AppException
from app.services.rules_reader import RulesReader


def _row(**overrides) -> dict:
    base = {
        "Field": "EORI Number",
        "Purpose": "...",
        "Mandatory/optional for compliance": "Mandatory",
        "Mandatory/optional for impact assessment": "No",
        "Data type/format": "Text (up to 17 chars)",
        "Validation rule": "...",
        "Example value": "DE123456789012345",
        "Minimum fields required for CBAM scope classification": "No",
        "Notes/assumptions": "...",
    }
    base.update(overrides)
    return base


@pytest.fixture
def reader() -> RulesReader:
    return RulesReader()


def test_required_when_compliance_column_is_mandatory(reader):
    df = pd.DataFrame([_row()])
    specs = reader.parse(df)
    assert len(specs) == 1
    assert specs[0].required is True


def test_required_when_impact_column_is_yes(reader):
    df = pd.DataFrame(
        [_row(Field="CN Code", **{"Mandatory/optional for compliance": "Optional", "Mandatory/optional for impact assessment": "Yes"})]
    )
    specs = reader.parse(df)
    assert specs[0].required is True


def test_not_required_when_both_columns_optional(reader):
    df = pd.DataFrame(
        [
            _row(
                Field="TARIC Code",
                **{"Mandatory/optional for compliance": "Optional", "Mandatory/optional for impact assessment": "No"},
            )
        ]
    )
    specs = reader.parse(df)
    assert specs[0].required is False


def test_required_strips_trailing_whitespace(reader):
    df = pd.DataFrame(
        [
            _row(
                **{"Mandatory/optional for compliance": "Mandatory ", "Mandatory/optional for impact assessment": " No "}
            )
        ]
    )
    specs = reader.parse(df)
    # The 'Mandatory' value should be recognised after stripping the trailing space.
    assert specs[0].required is True


def test_max_length_extracted_from_up_to_n_chars(reader):
    df = pd.DataFrame([_row(**{"Data type/format": "Text (up to 17 chars)"})])
    specs = reader.parse(df)
    assert specs[0].max_length == 17


def test_digit_pattern_extracted_from_numeric_n_digits(reader):
    df = pd.DataFrame([_row(Field="CN Code", **{"Data type/format": "Numeric (8 digits)"})])
    specs = reader.parse(df)
    assert specs[0].digit_pattern == r"^\d{8}$"


def test_digit_pattern_extracted_from_text_n_digits(reader):
    df = pd.DataFrame([_row(Field="TARIC Code", **{"Data type/format": "Text (10 digits)"})])
    specs = reader.parse(df)
    assert specs[0].digit_pattern == r"^\d{10}$"


def test_is_enum_detected(reader):
    df = pd.DataFrame([_row(Field="Product Type", **{"Data type/format": "Enum"})])
    specs = reader.parse(df)
    assert specs[0].is_enum is True
    assert specs[0].is_iso_3166 is False


def test_is_iso_3166_detected(reader):
    df = pd.DataFrame([_row(Field="Country of Origin", **{"Data type/format": "ISO 3166-1"})])
    specs = reader.parse(df)
    assert specs[0].is_iso_3166 is True
    assert specs[0].is_enum is False


def test_generic_data_type_leaves_attributes_default(reader):
    df = pd.DataFrame([_row(**{"Data type/format": "Text"})])
    specs = reader.parse(df)
    assert specs[0].max_length is None
    assert specs[0].digit_pattern is None
    assert specs[0].is_enum is False
    assert specs[0].is_iso_3166 is False


def test_missing_required_columns_raises(reader):
    df = pd.DataFrame([{"Field": "EORI Number"}])
    with pytest.raises(AppException) as exc:
        reader.parse(df)
    assert exc.value.status_code == 400
    assert "missing required columns" in exc.value.message


def test_empty_rows_are_skipped(reader):
    df = pd.DataFrame(
        [
            _row(),
            {"Field": None, "Data type/format": None},
            _row(Field="Notes / Comments"),
        ]
    )
    specs = reader.parse(df)
    assert [s.name for s in specs] == ["EORI Number", "Notes / Comments"]
