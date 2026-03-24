"""Context-aware policy engine for dynamic masking decisions."""
from ..models import Role, Purpose, MaskingStrategy

# Policy matrix: (role, purpose, consent) -> strategy
POLICY_RULES = {
    # Doctors
    (Role.DOCTOR, Purpose.TREATMENT, True):  (MaskingStrategy.FULL_ACCESS, "Doctor requesting treatment records with patient consent: Granted full access."),
    (Role.DOCTOR, Purpose.TREATMENT, False): (MaskingStrategy.PARTIAL_MASK, "Doctor requesting treatment records without patient consent: Granted partial access (identifiers masked)."),
    (Role.DOCTOR, Purpose.RESEARCH, True):   (MaskingStrategy.PARTIAL_MASK, "Doctor requesting research data with patient consent: Granted partial access (identifiers masked)."),
    (Role.DOCTOR, Purpose.RESEARCH, False):  (MaskingStrategy.FULL_ANONYMIZE, "Doctor requesting research data without patient consent: Granted anonymized access only."),
    (Role.DOCTOR, Purpose.BILLING, True):    (MaskingStrategy.DENY, "Access denied: Doctors are not authorized to retrieve records for billing purposes."),
    (Role.DOCTOR, Purpose.BILLING, False):   (MaskingStrategy.DENY, "Access denied: Doctors are not authorized to retrieve records for billing purposes."),
    (Role.DOCTOR, Purpose.LEGAL, True):      (MaskingStrategy.DENY, "Access denied: Doctors have no authorization for legal data retrieval."),
    (Role.DOCTOR, Purpose.LEGAL, False):     (MaskingStrategy.DENY, "Access denied: Doctors have no authorization for legal data retrieval."),
    (Role.DOCTOR, Purpose.PERSONAL, True):   (MaskingStrategy.DENY, "Access denied: Doctors cannot access patient records for personal reasons."),
    (Role.DOCTOR, Purpose.PERSONAL, False):  (MaskingStrategy.DENY, "Access denied: Doctors cannot access patient records for personal reasons."),

    # Nurses
    (Role.NURSE, Purpose.TREATMENT, True):   (MaskingStrategy.PARTIAL_MASK, "Nurse requesting treatment records with patient consent: Granted partial access (identifiers masked)."),
    (Role.NURSE, Purpose.TREATMENT, False):  (MaskingStrategy.PARTIAL_MASK, "Nurse requesting treatment records without patient consent: Granted partial access (identifiers masked)."),
    (Role.NURSE, Purpose.RESEARCH, True):    (MaskingStrategy.FULL_ANONYMIZE, "Nurse requesting research data with patient consent: Granted anonymized access only."),
    (Role.NURSE, Purpose.RESEARCH, False):   (MaskingStrategy.DENY, "Nurse requesting research data without patient consent: Access denied."),
    (Role.NURSE, Purpose.BILLING, True):     (MaskingStrategy.DENY, "Access denied: Nurses are not authorized for billing access."),
    (Role.NURSE, Purpose.BILLING, False):    (MaskingStrategy.DENY, "Access denied: Nurses are not authorized for billing access."),
    (Role.NURSE, Purpose.LEGAL, True):       (MaskingStrategy.DENY, "Access denied: Nurses are strictly prohibited from legal data retrieval."),
    (Role.NURSE, Purpose.LEGAL, False):      (MaskingStrategy.DENY, "Access denied: Nurses are strictly prohibited from legal data retrieval."),
    (Role.NURSE, Purpose.PERSONAL, True):    (MaskingStrategy.DENY, "Access denied: Nurses cannot access patient records for personal reasons."),
    (Role.NURSE, Purpose.PERSONAL, False):   (MaskingStrategy.DENY, "Access denied: Nurses cannot access patient records for personal reasons."),

    # Researchers
    (Role.RESEARCHER, Purpose.RESEARCH, True):  (MaskingStrategy.FULL_ANONYMIZE, "Researcher requesting research data with patient consent: Granted anonymized access only."),
    (Role.RESEARCHER, Purpose.RESEARCH, False): (MaskingStrategy.FULL_ANONYMIZE, "Researcher requesting research data without patient consent: Granted anonymized access only."),
    (Role.RESEARCHER, Purpose.TREATMENT, True): (MaskingStrategy.DENY, "Access denied: Researchers cannot access clinical treatment records."),
    (Role.RESEARCHER, Purpose.TREATMENT, False):(MaskingStrategy.DENY, "Access denied: Researchers cannot access clinical treatment records."),
    (Role.RESEARCHER, Purpose.BILLING, True):   (MaskingStrategy.DENY, "Access denied: Researchers are not authorized for financial or billing data."),
    (Role.RESEARCHER, Purpose.BILLING, False):  (MaskingStrategy.DENY, "Access denied: Researchers are not authorized for financial or billing data."),
    (Role.RESEARCHER, Purpose.LEGAL, True):     (MaskingStrategy.DENY, "Access denied: Researchers cannot retrieve data for legal purposes."),
    (Role.RESEARCHER, Purpose.LEGAL, False):    (MaskingStrategy.DENY, "Access denied: Researchers cannot retrieve data for legal purposes."),
    (Role.RESEARCHER, Purpose.PERSONAL, True):  (MaskingStrategy.DENY, "Access denied: Researchers cannot access patient records for personal reasons."),
    (Role.RESEARCHER, Purpose.PERSONAL, False): (MaskingStrategy.DENY, "Access denied: Researchers cannot access patient records for personal reasons."),

    # Patients
    (Role.PATIENT, Purpose.PERSONAL, True):  (MaskingStrategy.FULL_ACCESS, "Patient accessing personal records: Granted full access."),
    (Role.PATIENT, Purpose.PERSONAL, False): (MaskingStrategy.FULL_ACCESS, "Patient accessing personal records: Granted full access."),
    (Role.PATIENT, Purpose.TREATMENT, True): (MaskingStrategy.FULL_ACCESS, "Patient accessing treatment records: Granted full access."),
    (Role.PATIENT, Purpose.TREATMENT, False):(MaskingStrategy.FULL_ACCESS, "Patient accessing treatment records: Granted full access."),
    (Role.PATIENT, Purpose.RESEARCH, True):  (MaskingStrategy.DENY, "Access denied: Patients cannot perform cross-patient research."),
    (Role.PATIENT, Purpose.RESEARCH, False): (MaskingStrategy.DENY, "Access denied: Patients cannot perform cross-patient research."),
    (Role.PATIENT, Purpose.BILLING, True):   (MaskingStrategy.FULL_ACCESS, "Patient accessing their billing records: Granted full access."),
    (Role.PATIENT, Purpose.BILLING, False):  (MaskingStrategy.FULL_ACCESS, "Patient accessing their billing records: Granted full access."),
    (Role.PATIENT, Purpose.LEGAL, True):     (MaskingStrategy.FULL_ACCESS, "Patient retrieving records for legal reasons: Granted full access."),
    (Role.PATIENT, Purpose.LEGAL, False):    (MaskingStrategy.FULL_ACCESS, "Patient retrieving records for legal reasons: Granted full access."),

    # Companies
    (Role.COMPANY, Purpose.RESEARCH, True):  (MaskingStrategy.FULL_ANONYMIZE, "Company requesting research data with patient consent: Granted anonymized access only."),
    (Role.COMPANY, Purpose.RESEARCH, False): (MaskingStrategy.DENY, "Access denied: Companies require patient consent for research access."),
    (Role.COMPANY, Purpose.BILLING, True):   (MaskingStrategy.PARTIAL_MASK, "Company requesting billing records with patient consent: Granted partial access (identifiers dynamically masked)."),
    (Role.COMPANY, Purpose.BILLING, False):  (MaskingStrategy.DENY, "Access denied: Companies require patient consent for billing access."),
    (Role.COMPANY, Purpose.TREATMENT, True): (MaskingStrategy.DENY, "Access denied: Companies are prohibited from accessing medical treatment records."),
    (Role.COMPANY, Purpose.TREATMENT, False):(MaskingStrategy.DENY, "Access denied: Companies are prohibited from accessing medical treatment records."),
    (Role.COMPANY, Purpose.LEGAL, True):     (MaskingStrategy.DENY, "Access denied: Companies cannot retrieve records for legal purposes without a court order via Admin."),
    (Role.COMPANY, Purpose.LEGAL, False):    (MaskingStrategy.DENY, "Access denied: Companies cannot retrieve records for legal purposes without a court order via Admin."),
    (Role.COMPANY, Purpose.PERSONAL, True):  (MaskingStrategy.DENY, "Access denied: Companies cannot access patient records for personal reasons."),
    (Role.COMPANY, Purpose.PERSONAL, False): (MaskingStrategy.DENY, "Access denied: Companies cannot access patient records for personal reasons."),
}


def evaluate_policy(role: Role, purpose: Purpose, consent: bool) -> tuple:
    """Returns (MaskingStrategy, policy_explanation)."""
    key = (role, purpose, consent)
    if key in POLICY_RULES:
        return POLICY_RULES[key]
    # Default fallback: generate a smart, professional denial for any unmapped combinations
    consent_str = "even with patient consent" if consent else "without patient consent"
    role_name = role.value.capitalize()
    return (MaskingStrategy.DENY, f"Access denied: {role_name}s are not authorized to access patient records for {purpose.value} purposes, {consent_str}.")
