"""Date validator using strptime.

Params:
- ``format`` (str, optional): strptime format string. Defaults to ISO 8601
  (``%Y-%m-%d``).
"""
from __future__ import annotations

from datetime import datetime
from typing import Any


def validate(value: Any, params: dict) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str) and value.strip() == "":
        return []
    if isinstance(value, datetime):
        return []
    fmt = params.get("format", "%Y-%m-%d")
    try:
        datetime.strptime(str(value), fmt)
    except ValueError:
        return [f"Invalid date, expected format {fmt}"]
    return []
