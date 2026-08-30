"""Admin-only maintenance endpoints (temporary data pruning)."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ..security import CurrentUser, require_roles
from ..storage import store

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/purge")
def purge_data(user: CurrentUser = Depends(require_roles("admin"))):
    counts = store.purge_all(keep_admin=True)
    store.log_audit(
        action="PURGE", actor=user.username, actor_role=user.role,
        target="all", details=f"Purged: {counts}",
    )
    return {"purged": counts}
