"""Audit log endpoints."""
from fastapi import APIRouter
from ..models import AuditResponse, AuditEntry, StatsResponse
from ..services.storage import get_audit_logs, get_stats, get_all_patients

router = APIRouter(prefix="/api", tags=["audit"])


@router.get("/audit", response_model=AuditResponse)
def list_audit_logs(limit: int = 50, offset: int = 0):
    logs, total = get_audit_logs(limit, offset)
    return AuditResponse(
        logs=[AuditEntry(**l) for l in logs],
        total=total,
    )


@router.get("/stats", response_model=StatsResponse)
def get_system_stats():
    return StatsResponse(**get_stats())


@router.get("/patients")
def list_patients():
    return get_all_patients()
