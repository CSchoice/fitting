import io
import uuid
from typing import BinaryIO, Optional

import boto3
from botocore.client import Config

from app.config import settings


def _client():
    return boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4"),
        use_ssl=settings.s3_secure,
    )


def upload_bytes(data: bytes, key: Optional[str] = None, content_type: str = "application/octet-stream") -> str:
    s3 = _client()
    object_key = key or f"uploads/{uuid.uuid4().hex}"
    s3.put_object(
        Bucket=settings.s3_bucket,
        Key=object_key,
        Body=io.BytesIO(data),
        ContentType=content_type,
    )
    return object_key


def presigned_url(key: str, expires: int = 3600) -> str:
    s3 = _client()
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket, "Key": key},
        ExpiresIn=expires,
    )


