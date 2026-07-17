import uuid

from app.core.database import SessionLocal
from app.services.job_service import JobService
from app.services.ranking_service import RankingService, RankingWeights
from ml.chemistry.validity import DesignConstraints, filter_and_score_lipids
from workers.celery_app import celery_app

job_service = JobService()
ranking_service = RankingService()


@celery_app.task(name="design.run_job", bind=True)
def run_design_job(self, job_id: str, payload: dict) -> dict:
    """اجرای job طراحی لیپید با فیلتر RDKit و امتیازدهی اولیه."""
    db = SessionLocal()
    try:
        job = job_service.get(db, uuid.UUID(job_id))
        if job is None:
            raise ValueError(f"Job {job_id} not found")

        job_service.mark_running(db, job, celery_task_id=self.request.id)

        constraints_raw = payload.get("constraints", {})
        lipid_class = constraints_raw.get("lipid_class")
        constraints = DesignConstraints(
            max_molecular_weight=constraints_raw.get("max_molecular_weight", 800),
            min_log_p=constraints_raw.get("min_logP", 2.0),
            max_log_p=constraints_raw.get("max_logP", 8.0),
            lipid_class=lipid_class,
        )

        candidates = filter_and_score_lipids(constraints, lipid_class=lipid_class)

        from app.services.molecule_search_service import MoleculeSearchService

        search = MoleculeSearchService()
        for c in candidates:
            if c.get("smiles"):
                dedup = search.deduplicate(c["smiles"])
                c["is_duplicate"] = dedup["is_duplicate"]
                c["duplicate_of"] = dedup["duplicates"][:1]

        default_weights = RankingWeights()
        ranked = ranking_service.rank_candidates(candidates, default_weights)

        n_candidates = payload.get("n_candidates", len(ranked))
        ranked = ranked[:n_candidates]

        result = {
            "job_id": job_id,
            "status": "completed",
            "target_tissue": payload.get("target_tissue"),
            "cargo_type": payload.get("cargo_type"),
            "candidates": ranked,
            "filtered_count": len(candidates),
            "valid_count": sum(1 for c in candidates if c.get("synthesizable")),
        }
        job_service.mark_completed(db, job, result)
        return result
    except Exception as exc:
        job = job_service.get(db, uuid.UUID(job_id))
        if job is not None:
            job_service.mark_failed(db, job, str(exc))
        raise
    finally:
        db.close()
