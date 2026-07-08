"""Generic regex validator.

Params:
- ``pattern`` (str): the regular expression to match against the value.
- ``message`` (str, optional): error message returned on mismatch. Defaults
  to a generic "Does not match required format".
"""
from __future__ import annotations

import re
from typing import Any


def validate(value: Any, params: dict) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str) and value.strip() == "":
        return []
    pattern = params["pattern"]
    message = params.get("message", "Does not match required format")
    if not re.match(pattern, str(value)):
        return [message]
    return []
