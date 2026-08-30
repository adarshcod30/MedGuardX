"""Model-independent pattern recognizers.

These run the same way regardless of which spaCy model is loaded (sm / md / lg /
trf), because structured identifiers -- Aadhaar, PAN, MRN, credit cards -- are
matched by format, not by linguistic NER. This is what makes the "Indian PII"
support actually work: it never depended on the model in the first place.
"""
from __future__ import annotations

from typing import List

from presidio_analyzer import Pattern, PatternRecognizer

from .aadhaar import AadhaarRecognizer


def build_custom_recognizers() -> List[PatternRecognizer]:
    """Return the custom recognizers MedGuardX registers by default."""
    return [
        AadhaarRecognizer(),
        _pan_recognizer(),
        _mrn_recognizer(),
    ]


def _pan_recognizer() -> PatternRecognizer:
    """Indian Permanent Account Number: 5 letters, 4 digits, 1 letter (e.g. ABCDE1234F)."""
    return PatternRecognizer(
        supported_entity="IN_PAN",
        name="in_pan_recognizer",
        patterns=[
            Pattern(name="pan", regex=r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", score=0.85),
        ],
        context=["pan", "permanent account", "income tax"],
    )


def _mrn_recognizer() -> PatternRecognizer:
    """Medical Record Number.

    MRNs have no universal format, so we anchor on the explicit ``MRN``/``medical
    record`` context label followed by an alphanumeric code. Anchoring on the
    label keeps this precise instead of masking every stray number.
    """
    return PatternRecognizer(
        supported_entity="MEDICAL_RECORD_NUMBER",
        name="mrn_recognizer",
        patterns=[
            Pattern(
                name="mrn_labelled",
                regex=r"\b(?:MRN|Medical\s*Record\s*(?:No\.?|Number|#)?)[:\s#-]*([A-Z0-9][A-Z0-9-]{2,14})\b",
                score=0.8,
            ),
        ],
        context=["mrn", "medical record", "patient id", "chart"],
    )
