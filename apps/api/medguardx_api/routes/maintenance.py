"""Temporary admin-only cleanup endpoint. Removed immediately after use.

Deletes the leftover verification accounts created while testing the deploy, so
the production database returns to a clean state. Scoped to a username allow-list
rather than a blanket wipe.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ..security import CurrentUser, require_roles
from ..storage import store

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/cleanup")
def cleanup(user: CurrentUser = Depends(require_roles("admin"))):
    return {"deleted": store.delete_test_users()}
