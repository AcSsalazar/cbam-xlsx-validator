"""Unit tests for :class:`app.services.workbook_validator.WorkbookValidator`."""
from __future__ import annotations

import pandas as pd
import pytest

from app.core.exceptions import AppException
from app.schemas.workbook import FieldSpec
from app.services.workbook_validator import WorkbookValidator


@pytest.fixture
def validator() -> WorkbookValidator:
    return WorkbookValidator()


def _spec(name: str, required: bool = True) -> FieldSpec:
    return FieldSpec(name=name, required=required)


def test_matching_columns_pass(validator):
    df = pd.DataFrame(columns=["EORI Number", "CN Code"])
    specs = [_spec("EORI Number"), _spec("CN Code")]
    validator.validate(df, specs)  # should not raise


def test_extra_column_in_template_raises(validator):
    df = pd.DataFrame(columns=["EORI Number", "Unknown Column"])
    specs = [_spec("EORI Number")]
    with pytest.raises(AppException) as exc:
        validator.validate(df, specs)
    assert exc.value.status_code == 400
    assert "Unknown Column" in exc.value.message
    assert "not declared" in exc.value.message


def test_missing_column_in_template_raises(validator):
    df = pd.DataFrame(columns=["EORI Number"])
    specs = [_spec("EORI Number"), _spec("CN Code")]
    with pytest.raises(AppException) as exc:
        validator.validate(df, specs)
    assert exc.value.status_code == 400
    assert "CN Code" in exc.value.message
    assert "missing" in exc.value.message


def test_column_order_does_not_matter(validator):
    df = pd.DataFrame(columns=["CN Code", "EORI Number"])
    specs = [_spec("EORI Number"), _spec("CN Code")]
    validator.validate(df, specs)  # should not raise
