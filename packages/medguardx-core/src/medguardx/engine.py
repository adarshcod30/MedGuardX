"""The public MedGuardX engine -- a stateless facade over detection, policy and masking.

Typical use::

    from medguardx import MedGuardEngine, EngineConfig, Role, Purpose

    engine = MedGuardEngine(EngineConfig(model="en_core_web_md"))
    result = engine.process(
        "Patient John Smith, Aadhaar 2341 2341 2341, card 4111 1111 1111 1111.",
        role=Role.NURSE, purpose=Purpose.TREATMENT, consent=False,
    )
    print(result.masked_text)

The engine holds no data and does no I/O -- integrators own storage, auth and
audit. That statelessness is deliberate: it is what makes the engine safe to
embed anywhere.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .config import EngineConfig
from .detection import Detector, PIIEntity
from .enums import MaskingStrategy, Purpose, Role, coerce_purpose, coerce_role
from .masking import mask_text
from .policy import PolicyEngine


@dataclass
class ProcessResult:
    """Outcome of :meth:`MedGuardEngine.process`."""

    original_text: str
    masked_text: str
    entities: List[PIIEntity]
    strategy: MaskingStrategy
    policy_rule: str
    denied: bool = field(init=False)

    def __post_init__(self) -> None:
        self.denied = self.strategy == MaskingStrategy.DENY

    def to_dict(self) -> dict:
        return {
            "original_text": self.original_text,
            "masked_text": self.masked_text,
            "entities": [e.to_dict() for e in self.entities],
            "masking_strategy": self.strategy.value,
            "policy_rule": self.policy_rule,
            "entities_masked": 0 if self.strategy == MaskingStrategy.FULL_ACCESS else len(self.entities),
            "denied": self.denied,
        }


class MedGuardEngine:
    """Detect -> evaluate policy -> mask, in one call or as separate steps."""

    def __init__(
        self,
        config: Optional[EngineConfig] = None,
        policy: Optional[PolicyEngine] = None,
    ) -> None:
        self.config = config or EngineConfig()
        self.detector = Detector(self.config)
        self.policy = policy or PolicyEngine()

    # --- composable steps -------------------------------------------------------
    def detect(self, text: str) -> List[PIIEntity]:
        return self.detector.detect(text)

    def evaluate_policy(self, role, purpose, consent: bool):
        return self.policy.evaluate(role, purpose, consent)

    def mask(self, text: str, entities: List[PIIEntity], strategy: MaskingStrategy) -> str:
        return mask_text(text, entities, strategy)

    # --- one-shot ---------------------------------------------------------------
    def process(
        self,
        text: str,
        role,
        purpose,
        consent: bool = False,
        entities: Optional[List[PIIEntity]] = None,
    ) -> ProcessResult:
        """Run the full pipeline. Pass pre-computed ``entities`` to skip detection."""
        role = coerce_role(role)
        purpose = coerce_purpose(purpose)
        strategy, rule = self.policy.evaluate(role, purpose, consent)

        if strategy == MaskingStrategy.DENY:
            return ProcessResult(text, "", [], strategy, rule)

        detected = entities if entities is not None else self.detect(text)
        masked = self.mask(text, detected, strategy)
        return ProcessResult(text, masked, detected, strategy, rule)

    def warm_up(self) -> None:
        """Eagerly load the model (useful at service startup)."""
        self.detector._get_analyzer()
