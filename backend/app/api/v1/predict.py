from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_db, require_role
from app.core.security import Role
from app.schemas.predict import PredictOutcomeRequest, PredictOutcomeResponse
from app.services.predict_service import PredictService

router = APIRouter()
predict_service = PredictService()


@router.post("/outcome", response_model=PredictOutcomeResponse)
def predict_outcome(
    payload: PredictOutcomeRequest,
    db: Session = Depends(get_db),
    user: CurrentUser = Depends(require_role(Role.CLINICIAN)),
):
    """پیش‌بینی پیامد بالینی — با audit log و مدل CoxPH فعال."""
    try:
        return predict_service.predict_outcome(db, payload, user=user)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
