"""Aadhaar recognizer with Verhoeff checksum validation.

A 12-digit Aadhaar is easy to confuse with a phone number, an amount, or a date
if you match on shape alone -- that is exactly why the old build mis-tagged
Aadhaar as ``DATE_TIME``. Validating the Verhoeff checksum lets us assign a high
confidence score and win overlap resolution against the generic recognizers,
while keeping false positives low.
"""
from __future__ import annotations

import re
from typing import List, Optional

from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts

# Verhoeff algorithm tables.
_D = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
    [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
    [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
    [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
    [9, 8, 7, 6, 5, 4, 3, 2, 1, 0],
]
_P = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
    [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
    [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
    [7, 0, 4, 6, 9, 1, 3, 2, 5, 8],
]


def _verhoeff_valid(number: str) -> bool:
    c = 0
    for i, digit in enumerate(reversed(number)):
        c = _D[c][_P[i % 8][int(digit)]]
    return c == 0


# 12 digits, optionally grouped 4-4-4 by spaces or hyphens. First digit is 2-9.
# The lookarounds ensure the 12-digit run is not part of a LONGER grouped number
# (e.g. the first 12 digits of a 16-digit credit card) -- without them the
# recognizer would shadow CREDIT_CARD and leak the trailing group.
_AADHAAR_RE = re.compile(
    r"(?<!\d)(?<![\d][\s-])"           # not preceded by a digit or a digit-group separator
    r"[2-9][0-9]{3}[\s-]?[0-9]{4}[\s-]?[0-9]{4}"
    r"(?![\s-]?[0-9])"                  # not followed by another digit group
)


class AadhaarRecognizer(EntityRecognizer):
    """Detects Indian Aadhaar numbers, verified with the Verhoeff checksum."""

    def __init__(self) -> None:
        super().__init__(supported_entities=["IN_AADHAAR"], name="aadhaar_recognizer")

    def load(self) -> None:  # required by the EntityRecognizer contract
        return None

    def analyze(
        self, text: str, entities: List[str], nlp_artifacts: Optional[NlpArtifacts] = None
    ) -> List[RecognizerResult]:
        if "IN_AADHAAR" not in entities:
            return []

        results: List[RecognizerResult] = []
        for match in _AADHAAR_RE.finditer(text):
            digits = re.sub(r"[\s-]", "", match.group())
            if len(digits) != 12:
                continue
            # A valid Verhoeff checksum -> high confidence. A well-shaped but
            # unverified match still gets a moderate score so it is masked, just
            # with lower priority in overlap resolution.
            score = 0.9 if _verhoeff_valid(digits) else 0.5
            results.append(
                RecognizerResult(
                    entity_type="IN_AADHAAR",
                    start=match.start(),
                    end=match.end(),
                    score=score,
                    analysis_explanation=None,
                )
            )
        return results
