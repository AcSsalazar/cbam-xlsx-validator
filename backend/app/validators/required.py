"""Required-field validator.

Returns a single error if the value is ``None`` or a blank string.
"""
from __future__ import annotations

from typing import Any


def validate(value: Any, params: dict) -> list[str]:
    if value is None:
        return ["is required"]
    if isinstance(value, str) and value.strip() == "":
        return ["is required"]
    return []
