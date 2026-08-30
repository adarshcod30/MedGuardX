"""Core enumerations shared across the MedGuardX engine.

These are intentionally plain ``str`` enums so they serialize cleanly to JSON and
compare equal to their string values -- an integrator can pass ``"nurse"`` or
``Role.NURSE`` interchangeably.
"""
from __future__ import annotations

from enum import Enum


class Role(str, Enum):
    """Who is requesting the data."""

    DOCTOR = "doctor"
    NURSE = "nurse"
    RESEARCHER = "researcher"
    PATIENT = "patient"
    COMPANY = "company"
    ADMIN = "admin"


class Purpose(str, Enum):
    """Why the data is being requested."""

    TREATMENT = "treatment"
    RESEARCH = "research"
    BILLING = "billing"
    LEGAL = "legal"
    PERSONAL = "personal"


class MaskingStrategy(str, Enum):
    """How much of the data the requester is allowed to see."""

    FULL_ACCESS = "full_access"
    PARTIAL_MASK = "partial_mask"
    FULL_ANONYMIZE = "full_anonymize"
    DENY = "deny"


def coerce_role(value) -> "Role":
    return value if isinstance(value, Role) else Role(str(value).lower())


def coerce_purpose(value) -> "Purpose":
    return value if isinstance(value, Purpose) else Purpose(str(value).lower())
