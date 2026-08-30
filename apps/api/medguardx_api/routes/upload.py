"""Authenticated multi-format upload + PII detection."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from medguardx.ingestion import extract_text

from ..engine import get_engine
from ..schemas import PIIEntityOut, UploadResponse
from ..security import CurrentUser, get_current_user
from ..storage import store

router = APIRouter(prefix="/api", tags=["upload"])

MAX_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    patient_id: Optional[str] = Form(None),
    user: CurrentUser = Depends(get_current_user),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 10 MB limit")

    extracted, file_type = extract_text(file.filename or "data.txt", content)
    if not extracted.strip():
        raise HTTPException(status_code=400, detail=f"Could not extract readable text from the {file_type} file.")

    entities = get_engine().detect(extracted)

    if patient_id:
        if not store.patient_exists(patient_id):
            raise HTTPException(status_code=404, detail=f"Patient ID {patient_id} not found")
    else:
        patient_id = store.create_patient(owner_user_id=user.id)

    record_id = store.store_record(
        patient_id=patient_id,
        file_type=file_type,
        filename=file.filename or "unknown",
        extracted_text=extracted,
    )

    store.log_audit(
        action="UPLOAD", actor=user.username, actor_role=user.role, target=patient_id,
        details=f"Uploaded {file_type} '{file.filename}', {len(entities)} PII entities detected",
    )

    return UploadResponse(
        patient_id=patient_id,
        record_id=record_id,
        file_type=file_type,
        entities_detected=[PIIEntityOut(**e.to_dict()) for e in entities],
        message=f"Data ingested successfully. {len(entities)} PII entities detected.",
    )
