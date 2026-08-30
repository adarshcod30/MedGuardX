"""Engine configuration.

Everything an integrator might want to tune lives here. The most important knob
is ``model``: any installed spaCy English pipeline works (en_core_web_sm / md /
lg / trf). Nothing else in the engine changes when you swap it -- structured
identifiers are matched by regex recognizers that are model-independent.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

# Entities detected by default.
#
# NOTE: DATE_TIME is deliberately EXCLUDED from the default set. In the old build
# spaCy tagged nearly every digit run (phone numbers, Aadhaar, card numbers) as a
# high-confidence DATE_TIME, which hijacked the span and defeated the specialized
# recognizers -- the root cause of "some data gets masked, some not". Integrators
# who genuinely need date masking can add it back explicitly.
DEFAULT_ENTITIES: List[str] = [
    "PERSON",
    "PHONE_NUMBER",
    "EMAIL_ADDRESS",
    "CREDIT_CARD",
    "IBAN_CODE",
    "IP_ADDRESS",
    "LOCATION",
    "NRP",
    "MEDICAL_LICENSE",
    "URL",
    "US_SSN",
    # Custom, model-independent recognizers:
    "IN_AADHAAR",
    "IN_PAN",
    "MEDICAL_RECORD_NUMBER",
]

# Overlap-resolution priority. When two detections overlap, the one with the
# higher priority wins regardless of raw score. More specific / structured
# identifiers rank above generic linguistic ones so a phone number never loses to
# a stray PERSON or DATE_TIME span. Higher number = higher priority.
ENTITY_PRIORITY = {
    "IN_AADHAAR": 100,
    "IN_PAN": 100,
    "US_SSN": 100,
    "CREDIT_CARD": 95,
    "IBAN_CODE": 95,
    "MEDICAL_RECORD_NUMBER": 90,
    "MEDICAL_LICENSE": 85,
    "EMAIL_ADDRESS": 80,
    "PHONE_NUMBER": 75,
    "IP_ADDRESS": 70,
    "URL": 40,
    "PERSON": 60,
    "LOCATION": 55,
    "NRP": 50,
    "DATE_TIME": 20,
}


@dataclass
class EngineConfig:
    """Configuration for a :class:`~medguardx.engine.MedGuardEngine`.

    Attributes:
        model: Name of the installed spaCy pipeline to use. Pick per your
            accuracy/RAM trade-off: ``en_core_web_sm`` (~50MB, weakest),
            ``en_core_web_md`` (~120MB, recommended default), ``en_core_web_lg``
            (~600MB, best statistical), ``en_core_web_trf`` (transformer, highest
            accuracy, heaviest).
        score_threshold: Minimum confidence for a detection to be kept.
        entities: Which entity types to detect.
        enable_custom_recognizers: Register the Aadhaar/PAN/MRN recognizers.
        default_language: Language code passed to Presidio.
    """

    model: str = "en_core_web_md"
    score_threshold: float = 0.35
    entities: List[str] = field(default_factory=lambda: list(DEFAULT_ENTITIES))
    enable_custom_recognizers: bool = True
    default_language: str = "en"
