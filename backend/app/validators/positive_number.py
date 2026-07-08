"""Positive-number validator.

A value is valid when it can be parsed as ``float`` and the result is
strictly greater than zero.
"""
from __future__ import annotations

from typing import Any


def validate(value: Any, params: dict) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str) and value.strip() == "":
        return []
    try:
        number = float(value)
    except (TypeError, ValueError):
        return ["Must be a positive number"]
    if number <= 0:
        return ["Must be a positive number"]
    return []
