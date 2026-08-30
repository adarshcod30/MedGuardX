"""Request/response models for the API.

Note what is deliberately absent: the retrieve/upload request models do NOT carry
a ``role``. Role is derived from the authenticated token server-side, so a caller
can no longer choose their own privilege level.
"""
from __future__ import annotations

from typing import List, Optional

from medguardx import Purpose, Role
from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=8, max_length=256)
    role: Role = Role.PATIENT
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class PIIEntityOut(BaseModel):
    entity_type: str
    start: int
    end: int
    score: float
    text: str


class UploadResponse(BaseModel):
    patient_id: str
    record_id: int
    file_type: str
    entities_detected: List[PIIEntityOut]
    message: str


class RetrieveRequest(BaseModel):
    patient_id: str
    purpose: Purpose = Purpose.TREATMENT
    consent: bool = False  # role is taken from the token, never from here


class MaskedRecord(BaseModel):
    id: int
    file_type: str
    filename: Optional[str] = None
    masked_content: str


class RetrieveResponse(BaseModel):
    patient_id: str
    role: str
    masking_strategy: str
    records: List[MaskedRecord]
    entities_masked: int
    policy_rule: str


class PreviewRequest(BaseModel):
    text: str
    purpose: Purpose = Purpose.RESEARCH
    consent: bool = False  # role from token


class PreviewResponse(BaseModel):
    original_text: str
    masked_text: str
    entities: List[PIIEntityOut]
    masking_strategy: str
    policy_rule: str


class AuditEntry(BaseModel):
    id: int
    action: str
    actor: Optional[str]
    actor_role: Optional[str] = None
    target: Optional[str]
    details: Optional[str]
    timestamp: str


class AuditResponse(BaseModel):
    logs: List[AuditEntry]
    total: int


class StatsResponse(BaseModel):
    total_patients: int
    total_records: int
    total_access_events: int
    total_audit_logs: int
    recent_uploads: int
    recent_accesses: int
