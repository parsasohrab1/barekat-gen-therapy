import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.mlflow_tracking import log_training_run
from app.core.storage import download_pickle, upload_pickle
from app.models import ModelVersion
from ml.survival.coxph import CoxPHTrainResult, train_coxph


class ModelService:
    def train_and_store(
        self,
        db: Session,
        df,
        dataset_id: uuid.UUID,
        name: str = "coxph",
    ) -> ModelVersion:
        train_result: CoxPHTrainResult = train_coxph(df)
        version = self._next_version(db, name)
        model_id = uuid.uuid4()
        artifact_path = f"models/{name}/{version}/{model_id}.pkl"
        upload_pickle(artifact_path, train_result.model)

        metrics = {
            "c_index": train_result.c_index,
            "hazard_ratios": train_result.hazard_ratios,
            **train_result.summary,
        }

        mlflow_run_id = log_training_run(
            model_name=name,
            metrics={"c_index": train_result.c_index, "n_samples": len(df)},
            params={"version": version, "dataset_id": str(dataset_id)},
            artifact_path=artifact_path,
        )

        db.execute(update(ModelVersion).where(ModelVersion.name == name).values(is_active=False))

        model_version = ModelVersion(
            id=model_id,
            name=name,
            version=version,
            model_type="survival",
            metrics=metrics,
            artifact_path=artifact_path,
            dataset_id=dataset_id,
            is_active=True,
            trained_at=datetime.utcnow(),
            mlflow_run_id=mlflow_run_id,
        )
        db.add(model_version)
        db.commit()
        db.refresh(model_version)
        return model_version

    def get_active(self, db: Session, name: str = "coxph") -> ModelVersion | None:
        stmt = (
            select(ModelVersion)
            .where(ModelVersion.name == name, ModelVersion.is_active.is_(True))
            .order_by(ModelVersion.trained_at.desc())
        )
        return db.scalars(stmt).first()

    def list_models(self, db: Session) -> list[ModelVersion]:
        stmt = select(ModelVersion).order_by(ModelVersion.trained_at.desc())
        return list(db.scalars(stmt))

    def load_model(self, model_version: ModelVersion):
        return download_pickle(model_version.artifact_path)

    def _next_version(self, db: Session, name: str) -> str:
        stmt = select(ModelVersion).where(ModelVersion.name == name).order_by(ModelVersion.trained_at.desc())
        latest = db.scalars(stmt).first()
        if not latest:
            return "1.0.0"
        major, minor, patch = latest.version.split(".")
        return f"{major}.{minor}.{int(patch) + 1}"
