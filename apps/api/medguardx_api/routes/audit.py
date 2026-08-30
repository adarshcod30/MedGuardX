"""Audit, stats. Auditing is restricted to admin; stats to any authenticated user."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ..schemas import AuditEntry, AuditResponse, StatsResponse
from ..security import CurrentUser, get_current_user, require_roles
from ..storage import store

router = APIRouter(prefix="/api", tags=["audit"])


@router.get("/audit", response_model=AuditResponse)
def list_audit_logs(
    limit: int = 50,
    offset: int = 0,
    _: CurrentUser = Depends(require_roles("admin", "doctor")),
):
    limit = max(1, min(limit, 200))
    logs, total = store.get_audit_logs(limit, offset)
    return AuditResponse(logs=[AuditEntry(**l) for l in logs], total=total)


@router.get("/stats", response_model=StatsResponse)
def get_system_stats(_: CurrentUser = Depends(get_current_user)):
    return StatsResponse(**store.get_stats())
