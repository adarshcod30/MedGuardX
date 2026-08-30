"""Authenticated live masking sandbox. Role comes from the token."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ..engine import get_engine
from ..schemas import PIIEntityOut, PreviewRequest, PreviewResponse
from ..security import CurrentUser, get_current_user
from ..storage import store

router = APIRouter(prefix="/api", tags=["preview"])


@router.post("/preview", response_model=PreviewResponse)
def preview(body: PreviewRequest, user: CurrentUser = Depends(get_current_user)):
    result = get_engine().process(body.text, user.role, body.purpose, body.consent)

    store.log_audit(
        action="PREVIEW", actor=user.username, actor_role=user.role, target="(sandbox)",
        details=f"purpose={body.purpose.value} consent={body.consent} strategy={result.strategy.value}",
    )

    return PreviewResponse(
        original_text=result.original_text,
        masked_text=result.masked_text,
        entities=[PIIEntityOut(**e.to_dict()) for e in result.entities],
        masking_strategy=result.strategy.value,
        policy_rule=result.policy_rule,
    )
