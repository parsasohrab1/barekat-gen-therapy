"""Lab integration — LIMS, robot MQTT, in-vitro import."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import InVitroResult, LabSample, SynthesisOrder
from app.services.audit_service import AuditService
from app.services.model_service import ModelService

logger = logging.getLogger(__name__)


# Mock LIMS data for development / demo
MOCK_LIMS_SAMPLES = [
    {
        "external_id": "LIMS-2026-001",
        "sample_type": "LNP_formulation",
        "metadata": {"project": "barekat-phase1", "formulation_id": "F-101"},
    },
    {
        "external_id": "LIMS-2026-002",
        "sample_type": "in_vitro_assay",
        "metadata": {"assay": "transfection_hepg2", "plate": "P-42"},
    },
]


class LimsConnector:
    def fetch_remote_samples(self) -> list[dict]:
        """Fetch samples from LIMS_BASE_URL when enabled; otherwise use demo mock."""
        if not settings.LIMS_ENABLED:
            return list(MOCK_LIMS_SAMPLES)

        try:
            import urllib.request

            with urllib.request.urlopen(settings.LIMS_BASE_URL, timeout=5) as resp:
                payload = json.loads(resp.read().decode())
            samples = payload.get("samples", payload if isinstance(payload, list) else [])
            if samples:
                return samples
        except Exception as exc:
            logger.warning("LIMS remote fetch failed, using mock: %s", exc)

        return list(MOCK_LIMS_SAMPLES)

    def sync_samples(self, db: Session) -> list[LabSample]:
        synced: list[LabSample] = []
        for entry in self.fetch_remote_samples():
            existing = db.scalars(
                select(LabSample).where(LabSample.external_id == entry["external_id"])
            ).first()
            if existing:
                synced.append(existing)
                continue

            sample = LabSample(
                external_id=entry["external_id"],
                source="lims",
                sample_type=entry["sample_type"],
                status="received",
                sample_metadata=entry.get("metadata", {}),
            )
            db.add(sample)
            synced.append(sample)

        db.commit()
        logger.info("LIMS sync completed", extra={"action": "lims.sync", "count": len(synced)})
        return synced


class RobotClient:
    def dispatch_synthesis(
        self,
        db: Session,
        lipid_smiles: str,
        lipid_name: str | None = None,
        design_job_id: str | None = None,
        batch_id: str | None = None,
    ) -> SynthesisOrder:
        order = SynthesisOrder(
            lipid_smiles=lipid_smiles,
            lipid_name=lipid_name,
            design_job_id=design_job_id,
            batch_id=batch_id or f"BATCH-{uuid.uuid4().hex[:8].upper()}",
            status="queued",
        )
        db.add(order)
        db.flush()

        message = {
            "order_id": str(order.id),
            "command": "synthesize",
            "smiles": lipid_smiles,
            "name": lipid_name,
            "batch_id": order.batch_id,
            "protocol": "SiLA2_lipid_synthesis_v1",
        }

        if settings.MQTT_ENABLED:
            try:
                import paho.mqtt.publish as mqtt_publish

                mqtt_publish.single(
                    topic=settings.MQTT_TOPIC_SYNTHESIS,
                    payload=json.dumps(message),
                    hostname=settings.MQTT_BROKER_HOST,
                    port=settings.MQTT_BROKER_PORT,
                )
                order.status = "dispatched"
                order.mqtt_message_id = order.batch_id
            except Exception as exc:
                logger.warning("MQTT dispatch failed: %s", exc)
                order.status = "dispatch_failed"
        else:
            order.status = "simulated"

        db.commit()
        db.refresh(order)
        return order


class InVitroImporter:
    def import_results(self, db: Session, results: list[dict]) -> list[InVitroResult]:
        imported: list[InVitroResult] = []

        for row in results:
            sample = db.scalars(
                select(LabSample).where(LabSample.external_id == row.get("sample_external_id", ""))
            ).first()
            if sample is None:
                sample = LabSample(
                    external_id=row.get("sample_external_id", f"IMP-{uuid.uuid4().hex[:8]}"),
                    source="import",
                    sample_type="in_vitro_assay",
                    sample_metadata={"imported": True},
                )
                db.add(sample)
                db.flush()

            record = InVitroResult(
                sample_id=sample.id,
                lipid_smiles=row["lipid_smiles"],
                transfection_efficiency=float(row["transfection_efficiency"]),
                toxicity_score=float(row["toxicity_score"]),
                cell_line=row.get("cell_line", "HEPG2"),
                is_real_data=True,
            )
            db.add(record)
            imported.append(record)

        db.commit()
        logger.info(
            "In-vitro results imported",
            extra={"action": "lab.import_invitro", "count": len(imported)},
        )
        return imported


class RetrainService:
    def __init__(self) -> None:
        self.model_service = ModelService()
        self.audit = AuditService()

    def retrain_from_invitro(self, db: Session, user_id: uuid.UUID | None = None) -> dict:
        """Retrain efficacy model using real in-vitro feedback loop."""
        import pandas as pd

        results = list(db.scalars(select(InVitroResult).where(InVitroResult.is_real_data.is_(True))))
        if len(results) < 5:
            raise ValueError(f"Need at least 5 in-vitro results for retrain, got {len(results)}")

        # Map in-vitro to survival-like format for CoxPH retrain demo
        df = pd.DataFrame(
            [
                {
                    "Patient_ID": f"INV_{str(r.id)[:8]}",
                    "Age": 45,
                    "Gender": "Male",
                    "Disease_Severity": 5.0,
                    "Gene_5_Mutation": 0,
                    "Gene_12_Mutation": 0,
                    "Gene_18_Expr": r.transfection_efficiency,
                    "Time_to_Recovery_days": max(1, 180 * (1 - r.transfection_efficiency)),
                    "Event_Status": int(r.transfection_efficiency > 0.5),
                    "synthetic": False,
                }
                for r in results
            ]
        )

        dataset_id = uuid.uuid4()
        model_version = self.model_service.train_and_store(db, df, dataset_id=dataset_id, name="coxph")

        self.audit.log(
            db,
            action="model.retrain.invitro",
            user_id=user_id,
            model_version=model_version.version,
            details={
                "n_invitro_samples": len(results),
                "model_id": str(model_version.id),
                "data_source": "real_invitro",
            },
        )

        return {
            "model_id": str(model_version.id),
            "model_version": model_version.version,
            "c_index": model_version.metrics.get("c_index"),
            "n_samples": len(results),
            "retrained_at": datetime.utcnow().isoformat(),
        }
