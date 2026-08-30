"""PII/PHI detection built on Microsoft Presidio.

Two things here fix the old build's inconsistent masking:

1. The spaCy model is configurable (``EngineConfig.model``) instead of hardcoded.
2. Overlapping detections are resolved by a deterministic priority pass, so a
   specialized entity (phone, Aadhaar, card) can never be shadowed by a generic
   high-score span. In the old build the winner was whatever Presidio happened to
   score highest, which varied with phrasing -- the source of the flakiness.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List, Optional

from .config import ENTITY_PRIORITY, EngineConfig


@dataclass
class PIIEntity:
    """A single detected entity with its exact span in the source text."""

    entity_type: str
    start: int
    end: int
    score: float
    text: str

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict) -> "PIIEntity":
        return cls(
            entity_type=d["entity_type"],
            start=int(d["start"]),
            end=int(d["end"]),
            score=float(d["score"]),
            text=d.get("text", ""),
        )


class Detector:
    """Lazily-initialised Presidio analyzer wrapper.

    The heavy analyzer/model load happens on first use, not at import time, so
    importing :mod:`medguardx` stays cheap.
    """

    def __init__(self, config: Optional[EngineConfig] = None) -> None:
        self.config = config or EngineConfig()
        self._analyzer = None

    def _get_analyzer(self):
        if self._analyzer is not None:
            return self._analyzer

        from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
        from presidio_analyzer.nlp_engine import NlpEngineProvider

        provider = NlpEngineProvider(
            nlp_configuration={
                "nlp_engine_name": "spacy",
                "models": [{"lang_code": self.config.default_language, "model_name": self.config.model}],
            }
        )
        nlp_engine = provider.create_engine()

        registry = RecognizerRegistry()
        registry.load_predefined_recognizers(languages=[self.config.default_language])
        if self.config.enable_custom_recognizers:
            from .recognizers import build_custom_recognizers

            for recognizer in build_custom_recognizers():
                registry.add_recognizer(recognizer)

        self._analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine,
            registry=registry,
            supported_languages=[self.config.default_language],
        )
        return self._analyzer

    def detect(self, text: str, entities: Optional[List[str]] = None) -> List[PIIEntity]:
        """Detect PII entities in ``text`` and return a non-overlapping, sorted list."""
        if not text or not text.strip():
            return []

        analyzer = self._get_analyzer()
        raw = analyzer.analyze(
            text=text,
            language=self.config.default_language,
            entities=entities or self.config.entities,
            score_threshold=self.config.score_threshold,
        )

        found = [
            PIIEntity(
                entity_type=r.entity_type,
                start=r.start,
                end=r.end,
                score=round(float(r.score), 2),
                text=text[r.start : r.end],
            )
            for r in raw
        ]
        return resolve_overlaps(found)


def resolve_overlaps(entities: List[PIIEntity]) -> List[PIIEntity]:
    """Collapse overlapping spans, keeping the highest-priority entity per region.

    Priority is decided first by :data:`ENTITY_PRIORITY` (so a PHONE_NUMBER beats
    a DATE_TIME even at lower raw score), then by score, then by span length. The
    result is deterministic: the same text always yields the same masking.
    """
    if not entities:
        return []

    def rank(e: PIIEntity):
        return (ENTITY_PRIORITY.get(e.entity_type, 30), e.score, e.end - e.start)

    # Strongest candidates first; greedily accept ones that don't overlap an
    # already-accepted (higher-ranked) span.
    ordered = sorted(entities, key=rank, reverse=True)
    accepted: List[PIIEntity] = []
    for cand in ordered:
        if not any(cand.start < a.end and a.start < cand.end for a in accepted):
            accepted.append(cand)

    accepted.sort(key=lambda e: e.start)
    return accepted
