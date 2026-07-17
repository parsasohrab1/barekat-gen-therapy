from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_db, require_role
from app.core.security import Role
from app.schemas.model import ModelVersionResponse
from app.services.model_service import ModelService

router = APIRouter()
model_service = ModelService()


def _to_response(m) -> ModelVersionResponse:
    return ModelVersionResponse(
        model_id=str(m.id),
        name=m.name,
        version=m.version,
        model_type=m.model_type,
        metrics=m.metrics,
        is_active=m.is_active,
        dataset_id=str(m.dataset_id) if m.dataset_id else None,
        mlflow_run_id=m.mlflow_run_id,
        trained_at=m.trained_at,
    )


@router.get("", response_model=list[ModelVersionResponse])
def list_models(
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.VIEWER)),
):
    return [_to_response(m) for m in model_service.list_models(db)]


@router.get("/active", response_model=ModelVersionResponse)
def get_active_model(
    db: Session = Depends(get_db),
    _: CurrentUser = Depends(require_role(Role.VIEWER)),
    name: str = "coxph",
):
    model = model_service.get_active(db, name=name)
    if model is None:
        raise HTTPException(status_code=404, detail="No active model found")
    return _to_response(model)
