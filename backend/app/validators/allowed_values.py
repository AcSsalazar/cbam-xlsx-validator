"""Allowed-values validator.

Params:
- ``values`` (list): the set of acceptable values.
- ``message`` (str, optional): error message returned on mismatch.
"""
from __future__ import annotations

from typing import Any


def validate(value: Any, params: dict) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str) and value.strip() == "":
        return []
    values = params["values"]
    message = params.get("message", f"Must be one of: {', '.join(map(str, values))}")
    if value not in values:
        return [message]
    return []
