import uuid

from datetime import datetime



from sqlalchemy import select

from sqlalchemy.orm import Session



from app.core.storage import generate_presigned_url, upload_dataframe_parquet

from app.models import SyntheticDataset

from app.services.model_service import ModelService

from ml.evaluation.metrics import compute_recovery_histogram

from ml.synthetic.ck4gen import CK4GenPipeline

from ml.synthetic.generator import generate_gene_therapy_data





class SyntheticDataService:

    def __init__(self) -> None:

        self.model_service = ModelService()



    def run_pipeline(

        self,

        db: Session,

        job_id: uuid.UUID,

        n_patients: int,

        n_genes: int,

        seed: int,

        use_ck4gen: bool = True,

        n_clusters: int = 5,

    ) -> dict:

        if use_ck4gen:

            pipeline = CK4GenPipeline(n_clusters=n_clusters, seed=seed)

            ck4gen_result = pipeline.run(n_samples=n_patients, n_genes=n_genes)

            df = ck4gen_result.synthetic_df

            validation_metrics = {

                **ck4gen_result.validation,

                "pipeline": "ck4gen",

                "hazard_ratios": ck4gen_result.hazard_ratios,

                "n_clusters": ck4gen_result.n_clusters,

                "source_c_index": ck4gen_result.source_c_index,

            }

        else:

            df = generate_gene_therapy_data(n_patients=n_patients, n_genes=n_genes, seed=seed)

            df["synthetic"] = True

            validation_metrics = {"pipeline": "legacy"}



        dataset_id = uuid.uuid4()

        storage_path = f"datasets/synthetic/{dataset_id}.parquet"

        upload_dataframe_parquet(storage_path, df)



        histogram = compute_recovery_histogram(df["Time_to_Recovery_days"])

        validation_metrics.update(

            {

                "histogram": histogram,

                "mean_recovery_days": float(df["Time_to_Recovery_days"].mean()),

                "response_rate": float(df["Treatment_Response"].mean()),

                "event_rate": float(df["Event_Status"].mean()),

                "synthetic_label_rate": float(df["synthetic"].mean()) if "synthetic" in df.columns else 1.0,

            }

        )



        dataset = SyntheticDataset(

            id=dataset_id,

            job_id=job_id,

            n_samples=len(df),

            storage_path=storage_path,

            validation_metrics=validation_metrics,

            mean_recovery_days=float(df["Time_to_Recovery_days"].mean()),

            response_rate=float(df["Treatment_Response"].mean()),

            seed=seed,

            generated_at=datetime.utcnow(),

        )

        db.add(dataset)

        db.commit()



        model_version = self.model_service.train_and_store(db, df, dataset_id=dataset_id)



        return {

            "dataset_id": str(dataset_id),

            "model_id": str(model_version.id),

            "model_version": model_version.version,

            "n_samples": len(df),

            "mean_recovery_days": dataset.mean_recovery_days,

            "response_rate": dataset.response_rate,

            "c_index": model_version.metrics["c_index"],

            "hazard_ratios": model_version.metrics["hazard_ratios"],

            "histogram": histogram,

            "validation": validation_metrics,

            "download_url": generate_presigned_url(storage_path),

            "pipeline": validation_metrics.get("pipeline", "legacy"),

        }



    def get_dataset(self, db: Session, dataset_id: uuid.UUID) -> SyntheticDataset | None:

        return db.get(SyntheticDataset, dataset_id)



    def list_datasets(self, db: Session, limit: int = 50) -> list[SyntheticDataset]:

        stmt = select(SyntheticDataset).order_by(SyntheticDataset.generated_at.desc()).limit(limit)

        return list(db.scalars(stmt))


