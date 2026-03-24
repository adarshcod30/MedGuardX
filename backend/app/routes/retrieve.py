"""Retrieve endpoint with context-aware masking."""
from fastapi import APIRouter, HTTPException
from ..models import AccessRequest, RetrieveResponse, MaskingStrategy
from ..services.storage import get_records_by_patient, log_access, log_audit
from ..services.policy_engine import evaluate_policy
from ..services.masking import mask_text

router = APIRouter(prefix="/api", tags=["retrieve"])


@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve_data(req: AccessRequest):
    records = get_records_by_patient(req.patient_id)
    if not records:
        raise HTTPException(404, "No records found for this patient ID")

    # Evaluate policy
    strategy, policy_rule = evaluate_policy(req.role, req.purpose, req.consent)

    if strategy == MaskingStrategy.DENY:
        log_audit("ACCESS_DENIED", req.role.value, req.patient_id, policy_rule)
        raise HTTPException(403, f"Access denied: {policy_rule}")

    from ..services.pii_detection import detect_pii

    masked_records = []
    total_entities_masked = 0

    for r in records:
        text = r['extracted_text']
        # Use existing PII metadata or re-detect if missing to keep NLP context intact
        entities = r.get("pii_metadata")
        if not entities:
            from ..services.pii_detection import detect_pii
            entities = detect_pii(text)
        
        # Apply masking to this specific record text
        masked_text = mask_text(text, entities, strategy)
        
        from ..models import MaskedRecord
        masked_records.append(
            MaskedRecord(
                id=r['id'],
                file_type=r['file_type'],
                filename=r.get('original_filename', 'unknown'),
                masked_content=masked_text
            )
        )
        total_entities_masked += len(entities)

    # Log access
    for r in records:
        log_access(
            user_id=0, patient_id=req.patient_id, record_id=r["id"],
            role=req.role.value, purpose=req.purpose.value,
            consent=req.consent, masking_strategy=strategy.value,
            policy_rule=policy_rule
        )

    log_audit("RETRIEVE", req.role.value, req.patient_id,
              f"Strategy: {strategy.value} | Rule: {policy_rule}")

    return RetrieveResponse(
        patient_id=req.patient_id,
        masking_strategy=strategy.value,
        records=masked_records,
        entities_masked=total_entities_masked,
        policy_rule=policy_rule,
    )
