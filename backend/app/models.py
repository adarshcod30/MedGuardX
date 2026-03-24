"""Pydantic models for MedGuardX API."""
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class Role(str, Enum):
    DOCTOR = "doctor"
    NURSE = "nurse"
    RESEARCHER = "researcher"
    PATIENT = "patient"
    COMPANY = "company"
    ADMIN = "admin"


class Purpose(str, Enum):
    TREATMENT = "treatment"
    RESEARCH = "research"
    BILLING = "billing"
    LEGAL = "legal"
    PERSONAL = "personal"


class MaskingStrategy(str, Enum):
    FULL_ACCESS = "full_access"
    PARTIAL_MASK = "partial_mask"
    FULL_ANONYMIZE = "full_anonymize"
    DENY = "deny"


class UserCreate(BaseModel):
    username: str
    password: str
    role: Role = Role.PATIENT
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str


class PIIEntity(BaseModel):
    entity_type: str
    start: int
    end: int
    score: float
    text: str


class UploadResponse(BaseModel):
    patient_id: str
    record_id: int
    file_type: str
    entities_detected: List[PIIEntity]
    message: str


class AccessRequest(BaseModel):
    patient_id: str
    role: Role
    purpose: Purpose
    consent: bool = False


class MaskedRecord(BaseModel):
    id: int
    file_type: str
    filename: Optional[str] = None
    masked_content: str

class RetrieveResponse(BaseModel):
    patient_id: str
    masking_strategy: str
    records: List[MaskedRecord]
    entities_masked: int
    policy_rule: str


class PreviewRequest(BaseModel):
    text: str
    role: Role = Role.RESEARCHER
    purpose: Purpose = Purpose.RESEARCH
    consent: bool = False


class PreviewResponse(BaseModel):
    original_text: str
    masked_text: str
    entities: List[PIIEntity]
    masking_strategy: str
    policy_rule: str


class AuditEntry(BaseModel):
    id: int
    action: str
    actor: Optional[str]
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
