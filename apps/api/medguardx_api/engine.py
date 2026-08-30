"""Process-wide singleton MedGuardX engine.

One engine (and therefore one loaded spaCy model) is shared across all requests.
The model name comes from service config, so the deployment picks md while an
integrator running the container could pin any other model.
"""
from __future__ import annotations

from functools import lru_cache

from medguardx import EngineConfig, MedGuardEngine

from .config import get_settings


@lru_cache
def get_engine() -> MedGuardEngine:
    settings = get_settings()
    return MedGuardEngine(EngineConfig(model=settings.model))
