"""Context-aware policy engine.

Maps ``(role, purpose, consent)`` to a masking strategy plus a human-readable
rationale. The default matrix is the healthcare policy MedGuardX ships with;
integrators can subclass :class:`PolicyEngine` or pass a custom ``rules`` dict to
encode their own governance without touching detection or masking.
"""
from __future__ import annotations

from typing import Dict, Optional, Tuple

from .enums import MaskingStrategy, Purpose, Role, coerce_purpose, coerce_role

PolicyKey = Tuple[Role, Purpose, bool]
PolicyValue = Tuple[MaskingStrategy, str]

_FA = MaskingStrategy.FULL_ACCESS
_PM = MaskingStrategy.PARTIAL_MASK
_AN = MaskingStrategy.FULL_ANONYMIZE
_DN = MaskingStrategy.DENY

DEFAULT_RULES: Dict[PolicyKey, PolicyValue] = {
    # Doctors
    (Role.DOCTOR, Purpose.TREATMENT, True): (_FA, "Doctor requesting treatment records with patient consent: full access granted."),
    (Role.DOCTOR, Purpose.TREATMENT, False): (_PM, "Doctor requesting treatment records without consent: partial access (identifiers masked)."),
    (Role.DOCTOR, Purpose.RESEARCH, True): (_PM, "Doctor requesting research data with consent: partial access (identifiers masked)."),
    (Role.DOCTOR, Purpose.RESEARCH, False): (_AN, "Doctor requesting research data without consent: anonymized access only."),
    # Nurses
    (Role.NURSE, Purpose.TREATMENT, True): (_PM, "Nurse requesting treatment records with consent: partial access (identifiers masked)."),
    (Role.NURSE, Purpose.TREATMENT, False): (_PM, "Nurse requesting treatment records without consent: partial access (identifiers masked)."),
    (Role.NURSE, Purpose.RESEARCH, True): (_AN, "Nurse requesting research data with consent: anonymized access only."),
    # Researchers
    (Role.RESEARCHER, Purpose.RESEARCH, True): (_AN, "Researcher requesting research data with consent: anonymized access only."),
    (Role.RESEARCHER, Purpose.RESEARCH, False): (_AN, "Researcher requesting research data without consent: anonymized access only."),
    # Patients (own records)
    (Role.PATIENT, Purpose.PERSONAL, True): (_FA, "Patient accessing personal records: full access."),
    (Role.PATIENT, Purpose.PERSONAL, False): (_FA, "Patient accessing personal records: full access."),
    (Role.PATIENT, Purpose.TREATMENT, True): (_FA, "Patient accessing treatment records: full access."),
    (Role.PATIENT, Purpose.TREATMENT, False): (_FA, "Patient accessing treatment records: full access."),
    (Role.PATIENT, Purpose.BILLING, True): (_FA, "Patient accessing billing records: full access."),
    (Role.PATIENT, Purpose.BILLING, False): (_FA, "Patient accessing billing records: full access."),
    (Role.PATIENT, Purpose.LEGAL, True): (_FA, "Patient retrieving records for legal reasons: full access."),
    (Role.PATIENT, Purpose.LEGAL, False): (_FA, "Patient retrieving records for legal reasons: full access."),
    # Companies
    (Role.COMPANY, Purpose.RESEARCH, True): (_AN, "Company requesting research data with consent: anonymized access only."),
    (Role.COMPANY, Purpose.BILLING, True): (_PM, "Company requesting billing records with consent: partial access (identifiers masked)."),
    # Admins (governance / break-glass, still logged upstream)
    (Role.ADMIN, Purpose.LEGAL, True): (_FA, "Admin performing authorized legal retrieval: full access."),
    (Role.ADMIN, Purpose.LEGAL, False): (_FA, "Admin performing authorized legal retrieval: full access."),
}


class PolicyEngine:
    """Evaluates access policy. Deny-by-default for any unmapped combination."""

    def __init__(self, rules: Optional[Dict[PolicyKey, PolicyValue]] = None) -> None:
        self.rules = rules if rules is not None else dict(DEFAULT_RULES)

    def evaluate(self, role, purpose, consent: bool) -> PolicyValue:
        role = coerce_role(role)
        purpose = coerce_purpose(purpose)
        consent = bool(consent)

        hit = self.rules.get((role, purpose, consent))
        if hit is not None:
            return hit

        consent_str = "even with patient consent" if consent else "without patient consent"
        return (
            _DN,
            f"Access denied: {role.value.capitalize()}s are not authorized to access "
            f"records for {purpose.value} purposes, {consent_str}.",
        )
