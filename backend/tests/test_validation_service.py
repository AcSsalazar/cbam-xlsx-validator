"""Unit tests for :class:`app.services.validation_service.ValidationService`."""
from __future__ import annotations

import pandas as pd
import pytest

from app.schemas.workbook import FieldSpec
from app.services.validation_service import ValidationService


@pytest.fixture
def service() -> ValidationService:
    return ValidationService()


def _spec(name: str, **overrides) -> FieldSpec:
    defaults = {"required": True}
    defaults.update(overrides)
    return FieldSpec(name=name, **defaults)


def test_row_with_no_errors_is_kept(service):
    df = pd.DataFrame(
        {
            "EORI Number": ["DE123456789012345"],
            "CN Code": ["72071114"],
            "Import Volume": [1250],
            "Date of importation": ["05.05.2026"],
            "Product Type": ["Complex"],
            "Country of Origin": ["CN"],
        }
    )
    specs = [
        _spec("EORI Number", max_length=17),
        _spec("CN Code", digit_pattern=r"^\d{8}$"),
        _spec("Import Volume"),
        _spec("Date of importation"),
        _spec("Product Type"),
        _spec("Country of Origin", is_iso_3166=True),
    ]
    valid_df, errors = service.validate(df, specs)
    assert len(valid_df) == 1
    assert errors == []


def test_missing_required_field_produces_error(service):
    df = pd.DataFrame({"EORI Number": [None], "CN Code": ["72071114"]})
    specs = [_spec("EORI Number"), _spec("CN Code", digit_pattern=r"^\d{8}$")]
    valid_df, errors = service.validate(df, specs)
    assert len(valid_df) == 0
    assert len(errors) == 1
    assert errors[0].field == "EORI Number"
    assert errors[0].row == 2


def test_max_length_violation(service):
    df = pd.DataFrame({"EORI Number": ["A" * 25]})
    specs = [_spec("EORI Number", max_length=17)]
    valid_df, errors = service.validate(df, specs)
    assert len(valid_df) == 0
    assert "at most 17 characters" in errors[0].message


def test_digit_pattern_violation(service):
    df = pd.DataFrame({"CN Code": ["ABC123"]})
    specs = [_spec("CN Code", digit_pattern=r"^\d{8}$")]
    valid_df, errors = service.validate(df, specs)
    assert len(valid_df) == 0
    assert "digits" in errors[0].message


def test_iso_3166_violation(service):
    df = pd.DataFrame({"Country of Origin": ["XX"]})
    specs = [_spec("Country of Origin", is_iso_3166=True)]
    valid_df, errors = service.validate(df, specs)
    assert len(valid_df) == 0
    assert "ISO 3166" in errors[0].message


def test_iso_3166_accepts_valid_code(service):
    df = pd.DataFrame({"Country of Origin": ["CN", "US", "BR"]})
    specs = [_spec("Country of Origin", is_iso_3166=True)]
    valid_df, errors = service.validate(df, specs)
    assert len(valid_df) == 3
    assert errors == []


def test_hand_coded_eori_regex(service):
    df = pd.DataFrame(
        {
            "EORI Number": [
                "de123456789012345",  # lowercase country code -> fail
                "1A123456789012345",  # starts with a digit -> fail
                "DE",  # only country code, no body -> fail
                "DE123",  # valid (DE + 123)
            ]
        }
    )
    specs = [_spec("EORI Number")]
    valid_df, errors = service.validate(df, specs)
    assert len(valid_df) == 1
    assert {e.value for e in errors} == {
        "de123456789012345",
        "1A123456789012345",
        "DE",
    }


def test_hand_coded_date_format(service):
    df = pd.DataFrame({"Date of importation": ["05.05.2026", "2026-05-05", "abc"]})
    specs = [_spec("Date of importation")]
    valid_df, errors = service.validate(df, specs)
    assert len(valid_df) == 1
    assert len(errors) == 2


def test_hand_coded_positive_number(service):
    df = pd.DataFrame({"Import Volume": ["-50", "0", "12.5", "abc"]})
    specs = [_spec("Import Volume")]
    valid_df, errors = service.validate(df, specs)
    assert len(valid_df) == 1
    assert {e.value for e in errors} == {"-50", "0", "abc"}


def test_hand_coded_allowed_values(service):
    df = pd.DataFrame({"Product Type": ["Simple", "Complex", "Other"]})
    specs = [_spec("Product Type")]
    valid_df, errors = service.validate(df, specs)
    assert len(valid_df) == 2
    assert len(errors) == 1
    assert errors[0].value == "Other"


def test_optional_empty_field_does_not_produce_errors(service):
    df = pd.DataFrame({"Notes / Comments": [None, "", "Some comment"]})
    specs = [_spec("Notes / Comments", required=False)]
    valid_df, errors = service.validate(df, specs)
    assert len(valid_df) == 3
    assert errors == []


def test_mixed_valid_and_invalid_rows(service):
    df = pd.DataFrame(
        {
            # Row 0: both valid.
            # Row 1: EORI starts with a digit -> fail.
            # Row 2: CN Code not all digits -> fail.
            "EORI Number": ["DE123456789012345", "1A123456789012345", "DE123"],
            "CN Code": ["72071114", "72071114", "abc"],
        }
    )
    specs = [
        _spec("EORI Number", max_length=17),
        _spec("CN Code", digit_pattern=r"^\d{8}$"),
    ]
    valid_df, errors = service.validate(df, specs)
    assert len(valid_df) == 1
    assert list(valid_df["EORI Number"]) == ["DE123456789012345"]
    # The second row fails EORI; the third row fails CN Code.
    invalid_fields = {e.field for e in errors}
    assert "EORI Number" in invalid_fields
    assert "CN Code" in invalid_fields


def test_row_numbering_uses_two_index_based_offset(service):
    """The first data row in the Excel is row 2 (row 1 is the header)."""
    df = pd.DataFrame({"EORI Number": [None, "DE123456789012345", None]})
    specs = [_spec("EORI Number")]
    _, errors = service.validate(df, specs)
    assert [e.row for e in errors] == [2, 4]


def test_multiple_errors_per_row_collected(service):
    df = pd.DataFrame(
        {
            "EORI Number": ["TOOLONGEORI1234567890"],  # fails regex + max_length
            "CN Code": ["72071114"],  # valid
        }
    )
    specs = [
        _spec("EORI Number", max_length=17),
        _spec("CN Code", digit_pattern=r"^\d{8}$"),
    ]
    valid_df, errors = service.validate(df, specs)
    assert len(valid_df) == 0
    assert all(e.row == 2 for e in errors)
    assert len(errors) >= 2
