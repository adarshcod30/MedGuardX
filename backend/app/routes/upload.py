"""Upload endpoint for multi-format data ingestion."""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
from ..models import UploadResponse, PIIEntity
from ..services.ingestion import extract_text
from ..services.pii_detection import detect_pii
from ..services.storage import create_patient, check_patient_exists, store_record, log_audit

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    patient_id: Optional[str] = Form(None)
):
    content = await file.read()
    if not content:
        raise HTTPException(400, "Empty file")

    # Extract text
    extracted, file_type = extract_text(file.filename or "data.txt", content)
    if not extracted.strip():
        if file_type == 'pdf':
            raise HTTPException(400, "Could not extract text from PDF. If this is a scanned document (image-only PDF), please convert it to an image file (PNG/JPG) and upload again.")
        elif file_type == 'image':
            raise HTTPException(400, "No readable text detected by the OCR engine. Please ensure the image is clear and contains readable text.")
        else:
            raise HTTPException(400, "Could not extract any content from the file.")

    # Detect PII
    entities = detect_pii(extracted)

    # Validate or Create patient
    if patient_id:
        if not check_patient_exists(patient_id):
            raise HTTPException(404, f"Patient ID {patient_id} not found")
    else:
        patient_id = create_patient()

    record_id = store_record(
        patient_id=patient_id,
        file_type=file_type,
        filename=file.filename or "unknown",
        raw_data=content.decode('utf-8', errors='ignore'),
        extracted_text=extracted,
        pii_metadata=entities,
    )

    # Audit
    log_audit("UPLOAD", "system", patient_id,
              f"Uploaded {file_type} file '{file.filename}', {len(entities)} PII entities detected")

    return UploadResponse(
        patient_id=patient_id,
        record_id=record_id,
        file_type=file_type,
        entities_detected=[PIIEntity(**e) for e in entities],
        message=f"Data ingested successfully. {len(entities)} PII entities detected.",
    )
