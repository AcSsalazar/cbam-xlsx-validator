"""Unit tests for the individual validator functions."""
from __future__ import annotations

import pytest

from app.validators import (
    allowed_values,
    date,
    max_length,
    positive_number,
    regex,
    required,
)


# ---------- required ----------

@pytest.mark.parametrize("value", [None, "", "   ", "\t\n"])
def test_required_rejects_empty(value):
    assert required.validate(value, {}) == ["is required"]


@pytest.mark.parametrize("value", ["x", 0, 1, False, "0"])
def test_required_accepts_non_empty(value):
    assert required.validate(value, {}) == []


# ---------- max_length ----------

def test_max_length_within_limit():
    assert max_length.validate("abc", {"max": 5}) == []


def test_max_length_exceeds_limit():
    assert max_length.validate("abcdef", {"max": 5}) == [
        "Must be at most 5 characters"
    ]


def test_max_length_skips_empty():
    assert max_length.validate("", {"max": 5}) == []
    assert max_length.validate(None, {"max": 5}) == []


# ---------- regex ----------

def test_regex_matches():
    assert regex.validate("DE123", {"pattern": r"^[A-Z]{2}\d+$"}) == []


def test_regex_does_not_match():
    assert regex.validate("de123", {"pattern": r"^[A-Z]{2}\d+$"}) == [
        "Does not match required format"
    ]


def test_regex_custom_message():
    out = regex.validate(
        "de123",
        {"pattern": r"^[A-Z]{2}\d+$", "message": "Bad format"},
    )
    assert out == ["Bad format"]


def test_regex_skips_empty():
    assert regex.validate("", {"pattern": r".+"}) == []


# ---------- date ----------

def test_date_with_explicit_format():
    assert date.validate("05.05.2026", {"format": "%d.%m.%Y"}) == []


def test_date_with_wrong_format():
    out = date.validate("2026-05-05", {"format": "%d.%m.%Y"})
    assert "Invalid date" in out[0]


def test_date_with_default_iso_format():
    assert date.validate("2026-05-05", {}) == []


def test_date_skips_empty():
    assert date.validate("", {}) == []


# ---------- positive_number ----------

def test_positive_number_accepts_positive():
    assert positive_number.validate(1250, {}) == []
    assert positive_number.validate("12.5", {}) == []


def test_positive_number_rejects_zero_and_negative():
    assert positive_number.validate(0, {}) == ["Must be a positive number"]
    assert positive_number.validate(-50, {}) == ["Must be a positive number"]


def test_positive_number_rejects_non_numeric():
    assert positive_number.validate("abc", {}) == ["Must be a positive number"]


def test_positive_number_skips_empty():
    assert positive_number.validate("", {}) == []
    assert positive_number.validate(None, {}) == []


# ---------- allowed_values ----------

def test_allowed_values_accepts_member():
    assert allowed_values.validate("Simple", {"values": ["Simple", "Complex"]}) == []


def test_allowed_values_rejects_non_member():
    out = allowed_values.validate(
        "Other", {"values": ["Simple", "Complex"]}
    )
    assert "Simple" in out[0] and "Complex" in out[0]


def test_allowed_values_custom_message():
    out = allowed_values.validate(
        "X", {"values": ["A", "B"], "message": "Pick A or B"}
    )
    assert out == ["Pick A or B"]


def test_allowed_values_skips_empty():
    assert allowed_values.validate("", {"values": ["A"]}) == []
    assert allowed_values.validate(None, {"values": ["A"]}) == []
