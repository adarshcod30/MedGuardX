"""Authenticated, context-aware retrieval.

The requester's ROLE comes from the verified token (``user.role``) -- not from the
request body. Only ``purpose`` and ``consent`` are caller-supplied. PII is
re-detected fresh on the decrypted text each time, so masking never depends on
possibly-stale metadata captured at upload.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from medguardx import MaskingStrategy

from ..engine import get_engine
from ..schemas import MaskedRecord, RetrieveRequest, RetrieveResponse
from ..security import CurrentUser, get_current_user
from ..storage import store

router = APIRouter(prefix="/api", tags=["retrieve"])


@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve(body: RetrieveRequest, user: CurrentUser = Depends(get_current_user)):
    engine = get_engine()

    strategy, policy_rule = engine.evaluate_policy(user.role, body.purpose, body.consent)

    if strategy == MaskingStrategy.DENY:
        store.log_audit(
            action="ACCESS_DENIED", actor=user.username, actor_role=user.role,
            target=body.patient_id, details=policy_rule,
        )
        raise HTTPException(status_code=403, detail=policy_rule)

    records = store.get_records_by_patient(body.patient_id)
    if not records:
        raise HTTPException(status_code=404, detail="No records found for this patient ID")

    masked_records = []
    total_masked = 0
    for r in records:
        result = engine.process(r["extracted_text"], user.role, body.purpose, body.consent)
        masked_records.append(
            MaskedRecord(
                id=r["id"], file_type=r["file_type"],
                filename=r.get("original_filename") or "unknown",
                masked_content=result.masked_text,
            )
        )
        total_masked += 0 if strategy == MaskingStrategy.FULL_ACCESS else len(result.entities)
        store.log_access(
            user_id=user.id, username=user.username, patient_id=body.patient_id,
            record_id=r["id"], role=user.role, purpose=body.purpose.value,
            consent=body.consent, masking_strategy=strategy.value, policy_rule=policy_rule,
        )

    store.log_audit(
        action="RETRIEVE", actor=user.username, actor_role=user.role, target=body.patient_id,
        details=f"Strategy: {strategy.value} | {policy_rule}",
    )

    return RetrieveResponse(
        patient_id=body.patient_id,
        role=user.role,
        masking_strategy=strategy.value,
        records=masked_records,
        entities_masked=total_masked,
        policy_rule=policy_rule,
    )
