"""
Helpers for interacting with MinIO (S3-compatible object storage).
"""

from minio import Minio
from app.config import settings
import io


# Initialize a MinIO client using configuration from environment variables.
client = Minio(
    settings.MINIO_ENDPOINT,  # Hostname and port of the MinIO server.
    access_key=settings.MINIO_ACCESS_KEY,  # Access key credential.
    secret_key=settings.MINIO_SECRET_KEY,  # Secret key credential.
    # Convert the boolean MINIO_SECURE into the specific truthy strings MinIO expects.
    secure=str(settings.MINIO_SECURE).lower() in ("1", "true", "yes"),
)


def ensure_bucket(bucket: str) -> None:
    """
    Create a bucket if it does not already exist.

    This is safe to call every time before uploading an object.
    """

    # Query MinIO to see if the bucket is already available.
    if not client.bucket_exists(bucket):
        # If missing, create the bucket.
        client.make_bucket(bucket)


def upload_bytes(
    bucket: str,
    object_name: str,
    data: bytes,
    content_type: str = "application/octet-stream",
) -> str:
    """
    Upload a raw bytes payload to MinIO and return its accessible path.

    Args:
        bucket: Name of the MinIO bucket to store the object in.
        object_name: Key/path to give the object within the bucket.
        data: In-memory bytes to upload.
        content_type: MIME type of the object (e.g. "application/pdf").

    Returns:
        A string URL/path combining endpoint, bucket and object name.
    """

    # Ensure the target bucket exists before uploading.
    ensure_bucket(bucket)

    # Perform the upload, wrapping the bytes in a file-like buffer.
    client.put_object(
        bucket, object_name, io.BytesIO(data), length=len(data), content_type=content_type
    )

    # Construct and return a simple URL/path reference for later use.
    return f"{settings.MINIO_ENDPOINT}/{bucket}/{object_name}"

