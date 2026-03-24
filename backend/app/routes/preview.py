"""Preview endpoint for live masking demonstration."""
from fastapi import APIRouter
from ..models import PreviewRequest, PreviewResponse, PIIEntity
from ..services.pii_detection import detect_pii
from ..services.policy_engine import evaluate_policy
from ..services.masking import mask_text

router = APIRouter(prefix="/api", tags=["preview"])


@router.post("/preview", response_model=PreviewResponse)
def preview_masking(req: PreviewRequest):
    entities = detect_pii(req.text)
    strategy, policy_rule = evaluate_policy(req.role, req.purpose, req.consent)
    masked = mask_text(req.text, entities, strategy)

    return PreviewResponse(
        original_text=req.text,
        masked_text=masked,
        entities=[PIIEntity(**e) for e in entities],
        masking_strategy=strategy.value,
        policy_rule=policy_rule,
    )
