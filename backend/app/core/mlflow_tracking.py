"""MLflow experiment tracking integration."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


def log_training_run(
    model_name: str,
    metrics: dict,
    params: dict | None = None,
    artifact_path: str | None = None,
) -> str | None:
    if not settings.MLFLOW_ENABLED:
        return None

    try:
        import mlflow

        mlflow.set_tracking_uri(settings.MLFLOW_TRACKING_URI)
        mlflow.set_experiment("barekat-gen-therapy")

        with mlflow.start_run(run_name=f"{model_name}-train") as run:
            if params:
                mlflow.log_params(params)
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    mlflow.log_metric(key, value)
            if artifact_path:
                with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
                    tmp.write(f"artifact_path={artifact_path}\n".encode())
                    tmp_path = tmp.name
                mlflow.log_artifact(tmp_path, artifact_path="model")
                Path(tmp_path).unlink(missing_ok=True)

            logger.info(
                "MLflow run logged",
                extra={"action": "mlflow.log", "job_id": run.info.run_id},
            )
            return run.info.run_id
    except Exception as exc:
        logger.warning("MLflow logging failed: %s", exc)
        return None
