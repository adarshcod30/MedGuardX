"""Admin-only maintenance endpoint for pruning test/demo data.

Temporary: added to wipe synthetic verification data, removed afterwards.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ..security import CurrentUser, require_roles
from ..storage import store

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/purge")
def purge_data(user: CurrentUser = Depends(require_roles("admin"))):
    # keep_admin=False → full wipe, including the calling admin, for a clean slate.
    counts = store.purge_all(keep_admin=False)
    return {"purged": counts}
