"""PII/PHI detection using Microsoft Presidio."""
from typing import List, Dict

_analyzer = None

def _get_analyzer():
    global _analyzer
    if _analyzer is None:
        from presidio_analyzer import AnalyzerEngine
        from presidio_analyzer.nlp_engine import NlpEngineProvider
        configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        }
        provider = NlpEngineProvider(nlp_configuration=configuration)
        nlp_engine_instance = provider.create_engine()
        _analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine_instance, 
            supported_languages=["en"]
        )
    return _analyzer


def detect_pii(text: str) -> List[Dict]:
    """Detect PII entities in text using Presidio."""
    analyzer = _get_analyzer()
    results = analyzer.analyze(
        text=text,
        language="en",
        entities=[
            "PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS",
            "CREDIT_CARD", "IBAN_CODE", "IP_ADDRESS",
            "LOCATION", "DATE_TIME", "NRP",
            "MEDICAL_LICENSE", "URL",
            "IN_AADHAAR",  # Indian Aadhaar
            "IN_PAN",      # Indian PAN
        ],
    )

    entities = []
    for r in results:
        entities.append({
            "entity_type": r.entity_type,
            "start": r.start,
            "end": r.end,
            "score": round(r.score, 2),
            "text": text[r.start:r.end],
        })

    # Sort by position
    entities.sort(key=lambda x: x["start"])
    return entities
