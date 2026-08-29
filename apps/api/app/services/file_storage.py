"""MinIO (S3-compatible) file storage helpers.

Keep the signatures of `upload_file`, `download_file`, and `delete_file` stable —
the RAG ingestion pipeline (owned by another agent) depends on them.
"""
import uuid

import aioboto3
from botocore.exceptions import ClientError

from app.core.config import settings

_session = aioboto3.Session()

_BUCKET_ALREADY_EXISTS_CODES = {"BucketAlreadyOwnedByYou", "BucketAlreadyExists"}


def _client_kwargs() -> dict:
    scheme = "https" if settings.minio_secure else "http"
    return {
        "endpoint_url": f"{scheme}://{settings.minio_endpoint}",
        "aws_access_key_id": settings.minio_access_key,
        "aws_secret_access_key": settings.minio_secret_key,
    }


async def _ensure_bucket(s3) -> None:
    try:
        await s3.create_bucket(Bucket=settings.minio_bucket)
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "")
        if error_code not in _BUCKET_ALREADY_EXISTS_CODES:
            raise


async def upload_file(
    org_id: uuid.UUID,
    kb_id: uuid.UUID,
    document_id: uuid.UUID,
    filename: str,
    content: bytes,
) -> str:
    """Uploads to MinIO, returns the storage_path (object key)."""
    storage_path = f"{org_id}/{kb_id}/{document_id}/{filename}"
    async with _session.client("s3", **_client_kwargs()) as s3:
        await _ensure_bucket(s3)
        await s3.put_object(Bucket=settings.minio_bucket, Key=storage_path, Body=content)
    return storage_path


async def download_file(storage_path: str) -> bytes:
    """Downloads object bytes from MinIO."""
    async with _session.client("s3", **_client_kwargs()) as s3:
        response = await s3.get_object(Bucket=settings.minio_bucket, Key=storage_path)
        body = await response["Body"].read()
    return body


async def delete_file(storage_path: str) -> None:
    async with _session.client("s3", **_client_kwargs()) as s3:
        await s3.delete_object(Bucket=settings.minio_bucket, Key=storage_path)
