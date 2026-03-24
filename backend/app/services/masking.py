"""Masking engine using Presidio Anonymizer."""
from typing import List, Dict
from ..models import MaskingStrategy

_anonymizer = None

def _get_anonymizer():
    global _anonymizer
    if _anonymizer is None:
        from presidio_anonymizer import AnonymizerEngine
        _anonymizer = AnonymizerEngine()
    return _anonymizer


def mask_text(text: str, entities: List[Dict], strategy: MaskingStrategy) -> str:
    """Apply masking to text based on strategy."""
    if strategy == MaskingStrategy.FULL_ACCESS:
        return text
    if strategy == MaskingStrategy.DENY:
        return "[ACCESS DENIED — Insufficient permissions]"

    from presidio_anonymizer.entities import RecognizerResult, OperatorConfig
    from presidio_analyzer import RecognizerResult as AnalyzerResult

    analyzer_results = []
    for e in entities:
        analyzer_results.append(
            AnalyzerResult(
                entity_type=e["entity_type"],
                start=e["start"],
                end=e["end"],
                score=e["score"],
            )
        )

    if not analyzer_results:
        return text

    anonymizer = _get_anonymizer()

    if strategy == MaskingStrategy.FULL_ANONYMIZE:
        operators = {
            "DEFAULT": OperatorConfig("replace", {"new_value": "[REDACTED]"}),
            "PERSON": OperatorConfig("replace", {"new_value": "[NAME_REDACTED]"}),
            "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[PHONE_REDACTED]"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL_REDACTED]"}),
            "LOCATION": OperatorConfig("replace", {"new_value": "[LOCATION_REDACTED]"}),
            "IN_AADHAAR": OperatorConfig("replace", {"new_value": "[AADHAAR_REDACTED]"}),
            "IN_PAN": OperatorConfig("replace", {"new_value": "[PAN_REDACTED]"}),
        }
    else:  # PARTIAL_MASK
        operators = {
            "DEFAULT": OperatorConfig("mask", {"masking_char": "*", "chars_to_mask": 8, "from_end": False}),
            "PERSON": OperatorConfig("replace", {"new_value": "[NAME_MASKED]"}),
            "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[PHONE_MASKED]"}),
            "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL_MASKED]"}),
            "IN_AADHAAR": OperatorConfig("replace", {"new_value": "[AADHAAR_MASKED]"}),
            "IN_PAN": OperatorConfig("replace", {"new_value": "[PAN_MASKED]"}),
        }

    result = anonymizer.anonymize(
        text=text,
        analyzer_results=analyzer_results,
        operators=operators,
    )
    return result.text
