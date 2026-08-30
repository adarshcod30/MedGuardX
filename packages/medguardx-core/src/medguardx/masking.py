"""Deterministic, leak-proof masking.

The old build delegated to Presidio's anonymizer with a DEFAULT operator that
masked only the first 8 characters -- so a 19-digit card came back as
``********1 1111 1111`` and IPs/IBANs leaked their tails. Here we do span
replacement ourselves over the already-de-overlapped entity list, replacing from
right to left so indices stay valid. The invariant is simple and testable: for
any strategy other than FULL_ACCESS, the original entity substring never survives
in the output.
"""
from __future__ import annotations

from typing import Callable, Dict, List

from .detection import PIIEntity
from .enums import MaskingStrategy

# Human-readable label per entity type, used in redaction tokens.
_LABELS: Dict[str, str] = {
    "PERSON": "NAME",
    "PHONE_NUMBER": "PHONE",
    "EMAIL_ADDRESS": "EMAIL",
    "CREDIT_CARD": "CARD",
    "IBAN_CODE": "IBAN",
    "IP_ADDRESS": "IP",
    "LOCATION": "LOCATION",
    "URL": "URL",
    "NRP": "NRP",
    "US_SSN": "SSN",
    "MEDICAL_LICENSE": "MED_LICENSE",
    "MEDICAL_RECORD_NUMBER": "MRN",
    "IN_AADHAAR": "AADHAAR",
    "IN_PAN": "PAN",
    "DATE_TIME": "DATE",
}

DENY_MESSAGE = "[ACCESS DENIED - Insufficient permissions]"


def _label(entity_type: str) -> str:
    return _LABELS.get(entity_type, entity_type)


def _redact(entity: PIIEntity) -> str:
    return f"[{_label(entity.entity_type)}_REDACTED]"


# --- Partial-mask reveal helpers -------------------------------------------------
# Partial masking trades a *small, bounded* amount of the original for downstream
# utility (e.g. matching a card by its last 4). Every helper below reveals at most
# a safe suffix and masks everything else; none can leave the majority visible.

def _reveal_last(value: str, keep: int, ch: str = "*") -> str:
    digits = [c for c in value if c.isalnum()]
    if len(digits) <= keep:
        return ch * len(digits)
    return ch * (len(digits) - keep) + "".join(digits[-keep:])


def _partial_card(entity: PIIEntity) -> str:
    return f"[CARD ****{_reveal_last(entity.text, 4)[-4:]}]"


def _partial_phone(entity: PIIEntity) -> str:
    return f"[PHONE ****{_reveal_last(entity.text, 2)[-2:]}]"


def _partial_email(entity: PIIEntity) -> str:
    local, _, domain = entity.text.partition("@")
    if not domain:
        return "[EMAIL_MASKED]"
    hint = (local[:1] + "***") if local else "***"
    return f"{hint}@{domain}"


# Types that get a partial reveal under PARTIAL_MASK. Everything else is fully
# redacted even under partial masking -- safe by default.
_PARTIAL_OPERATORS: Dict[str, Callable[[PIIEntity], str]] = {
    "CREDIT_CARD": _partial_card,
    "PHONE_NUMBER": _partial_phone,
    "EMAIL_ADDRESS": _partial_email,
}


def _mask_token(entity: PIIEntity, strategy: MaskingStrategy) -> str:
    if strategy == MaskingStrategy.PARTIAL_MASK and entity.entity_type in _PARTIAL_OPERATORS:
        return _PARTIAL_OPERATORS[entity.entity_type](entity)
    return _redact(entity)


def mask_text(text: str, entities: List[PIIEntity], strategy: MaskingStrategy) -> str:
    """Apply ``strategy`` to ``text`` given its detected ``entities``."""
    if strategy == MaskingStrategy.FULL_ACCESS:
        return text
    if strategy == MaskingStrategy.DENY:
        return DENY_MESSAGE
    if not entities:
        return text

    # Replace right-to-left so earlier spans keep their original indices.
    ordered = sorted(entities, key=lambda e: e.start, reverse=True)
    out = text
    for e in ordered:
        if e.start < 0 or e.end > len(out) or e.start >= e.end:
            continue  # stale/invalid span -- skip rather than corrupt the text
        out = out[: e.start] + _mask_token(e, strategy) + out[e.end :]
    return out
