"""Qdrant vector store for molecular similarity search."""

from __future__ import annotations

import logging
import uuid

from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self) -> None:
        self._client = None

    @property
    def client(self):
        if self._client is None and settings.QDRANT_ENABLED:
            from qdrant_client import QdrantClient

            self._client = QdrantClient(url=settings.QDRANT_URL)
        return self._client

    def ensure_collection(self, vector_size: int = 2048) -> None:
        if not settings.QDRANT_ENABLED or self.client is None:
            return
        from qdrant_client.models import Distance, VectorParams

        collections = [c.name for c in self.client.get_collections().collections]
        if settings.QDRANT_COLLECTION not in collections:
            self.client.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    def upsert_molecule(
        self,
        smiles: str,
        vector: list[float],
        payload: dict,
        point_id: str | None = None,
    ) -> str:
        if not settings.QDRANT_ENABLED or self.client is None:
            return point_id or str(uuid.uuid4())

        from qdrant_client.models import PointStruct

        self.ensure_collection(len(vector))
        pid = point_id or str(uuid.uuid5(uuid.NAMESPACE_URL, smiles))
        self.client.upsert(
            collection_name=settings.QDRANT_COLLECTION,
            points=[PointStruct(id=pid, vector=vector, payload={"smiles": smiles, **payload})],
        )
        return pid

    def search_similar(self, vector: list[float], limit: int = 10, threshold: float = 0.7) -> list[dict]:
        if not settings.QDRANT_ENABLED or self.client is None:
            return []

        results = self.client.search(
            collection_name=settings.QDRANT_COLLECTION,
            query_vector=vector,
            limit=limit,
            score_threshold=threshold,
        )
        return [
            {
                "id": str(hit.id),
                "score": float(hit.score),
                "smiles": hit.payload.get("smiles"),
                **{k: v for k, v in hit.payload.items() if k != "smiles"},
            }
            for hit in results
        ]

    def find_duplicates(self, vector: list[float], threshold: float = 0.95) -> list[dict]:
        return self.search_similar(vector, limit=5, threshold=threshold)
