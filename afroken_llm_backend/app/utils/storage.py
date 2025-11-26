from minio import Minio
from app.config import settings
import io


client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=str(settings.MINIO_SECURE).lower() in ("1", "true", "yes"),
)


def ensure_bucket(bucket: str) -> None:
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)


def upload_bytes(
    bucket: str,
    object_name: str,
    data: bytes,
    content_type: str = "application/octet-stream",
) -> str:
    ensure_bucket(bucket)
    client.put_object(
        bucket, object_name, io.BytesIO(data), length=len(data), content_type=content_type
    )
    return f"{settings.MINIO_ENDPOINT}/{bucket}/{object_name}"



