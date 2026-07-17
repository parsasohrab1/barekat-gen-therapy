from sqlalchemy.orm import Session

from app.api.deps import CurrentUser
from app.schemas.predict import PredictOutcomeRequest, PredictOutcomeResponse
from app.services.audit_service import AuditService
from app.services.model_service import ModelService
from ml.survival.coxph import predict_outcome


class PredictService:
    def __init__(self) -> None:
        self.model_service = ModelService()
        self.audit = AuditService()

    def predict_outcome(
        self,
        db: Session,
        payload: PredictOutcomeRequest,
        user: CurrentUser | None = None,
    ) -> PredictOutcomeResponse:
        model_version = self.model_service.get_active(db)
        if model_version is None:
            raise ValueError("No trained CoxPH model available. Run synthetic data generation first.")

        model = self.model_service.load_model(model_version)
        patient = payload.model_dump()
        result = predict_outcome(model, patient)

        response = PredictOutcomeResponse(
            time_to_recovery_days=result["time_to_recovery_days"],
            event_probability=result["event_probability"],
            toxicity_level=result["toxicity_level"],
            model_version=model_version.version,
            partial_hazard=result["partial_hazard"],
            is_research_prediction=True,
        )

        self.audit.log_clinical_decision(
            db,
            user_id=user.id if user else None,
            decision_type="outcome_prediction",
            model_version=model_version.version,
            input_payload=patient,
            outcome=response.model_dump(),
        )

        return response
