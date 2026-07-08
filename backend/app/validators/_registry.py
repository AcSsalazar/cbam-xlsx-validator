"""Registry mapping rule names to their ``validate`` functions.

Used by :mod:`app.services.validation_service` to dispatch validation by
name. Each entry references a function in the ``app.validators`` package
with the uniform signature ``validate(value, params) -> list[str]``.
"""
from __future__ import annotations

from app.validators import (
    allowed_values,
    date,
    max_length,
    positive_number,
    regex,
    required,
)

VALIDATORS = {
    "required": required.validate,
    "max_length": max_length.validate,
    "regex": regex.validate,
    "date": date.validate,
    "positive_number": positive_number.validate,
    "allowed_values": allowed_values.validate,
}


def get(name: str):
    """Return the validator function for ``name`` or ``None`` if unknown."""
    return VALIDATORS.get(name)
