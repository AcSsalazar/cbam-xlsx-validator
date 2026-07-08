"""Maximum string length validator.

Params:
- ``max`` (int): inclusive maximum length.
"""
from __future__ import annotations

from typing import Any


def validate(value: Any, params: dict) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str) and value.strip() == "":
        return []
    maximum = params["max"]
    if len(str(value)) > maximum:
        return [f"Must be at most {maximum} characters"]
    return []
