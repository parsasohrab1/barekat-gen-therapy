"""MinIO / S3-compatible object storage client."""

import io
import pickle
from functools import lru_cache
from typing import Any

import boto3
import pandas as pd
from botocore.client import BaseClient
from botocore.config import Config
from botocore.exceptions import ClientError

from app.core.config import settings


@lru_cache
def get_s3_client() -> BaseClient:
    protocol = "https" if settings.MINIO_SECURE else "http"
    return boto3.client(
        "s3",
        endpoint_url=f"{protocol}://{settings.MINIO_ENDPOINT}",
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def ensure_bucket() -> None:
    client = get_s3_client()
    try:
        buckets = [b["Name"] for b in client.list_buckets().get("Buckets", [])]
        if settings.MINIO_BUCKET not in buckets:
            client.create_bucket(Bucket=settings.MINIO_BUCKET)
    except ClientError:
        pass


def upload_bytes(key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    ensure_bucket()
    client = get_s3_client()
    client.put_object(Bucket=settings.MINIO_BUCKET, Key=key, Body=data, ContentType=content_type)
    return key


def upload_dataframe_parquet(key: str, df: pd.DataFrame) -> str:
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    return upload_bytes(key, buffer.getvalue(), content_type="application/octet-stream")


def upload_pickle(key: str, obj: Any) -> str:
    return upload_bytes(key, pickle.dumps(obj), content_type="application/octet-stream")


def download_bytes(key: str) -> bytes:
    client = get_s3_client()
    response = client.get_object(Bucket=settings.MINIO_BUCKET, Key=key)
    return response["Body"].read()


def download_pickle(key: str) -> Any:
    return pickle.loads(download_bytes(key))


def download_dataframe_parquet(key: str) -> pd.DataFrame:
    return pd.read_parquet(io.BytesIO(download_bytes(key)))


def generate_presigned_url(key: str, expires_in: int = 3600) -> str:
    client = get_s3_client()
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.MINIO_BUCKET, "Key": key},
        ExpiresIn=expires_in,
    )
