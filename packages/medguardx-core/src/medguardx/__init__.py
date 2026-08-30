"""MedGuardX core -- context-aware PII/PHI detection and masking.

Public API::

    from medguardx import (
        MedGuardEngine, EngineConfig, ProcessResult,
        PolicyEngine, PIIEntity,
        Role, Purpose, MaskingStrategy,
    )
"""
from __future__ import annotations

from .config import DEFAULT_ENTITIES, EngineConfig
from .detection import Detector, PIIEntity, resolve_overlaps
from .engine import MedGuardEngine, ProcessResult
from .enums import MaskingStrategy, Purpose, Role
from .masking import mask_text
from .policy import DEFAULT_RULES, PolicyEngine

__version__ = "1.0.0"

__all__ = [
    "MedGuardEngine",
    "EngineConfig",
    "ProcessResult",
    "Detector",
    "PIIEntity",
    "resolve_overlaps",
    "PolicyEngine",
    "DEFAULT_RULES",
    "DEFAULT_ENTITIES",
    "mask_text",
    "Role",
    "Purpose",
    "MaskingStrategy",
    "__version__",
]
