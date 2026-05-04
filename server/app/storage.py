import os
import base64
import uuid
import boto3
from botocore.config import Config

def _client():
    account_id = os.getenv("R2_ACCOUNT_ID")
    return boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )

def upload_base64_image(b64_data: str, prefix: str = "plants") -> str:
    """Upload a base64 image string to R2, return its public URL."""
    if "," in b64_data:
        header, b64_data = b64_data.split(",", 1)
        ext = "jpg"
        if "png" in header:
            ext = "png"
        elif "webp" in header:
            ext = "webp"
    else:
        ext = "jpg"

    image_bytes = base64.b64decode(b64_data)
    key = f"{prefix}/{uuid.uuid4()}.{ext}"
    bucket = os.getenv("R2_BUCKET_NAME")

    _client().put_object(
        Bucket=bucket,
        Key=key,
        Body=image_bytes,
        ContentType=f"image/{ext}",
    )

    public_url = os.getenv("R2_PUBLIC_URL", "").rstrip("/")
    return f"{public_url}/{key}"

def delete_image(url: str):
    """Delete an image from R2 given its public URL."""
    public_url = os.getenv("R2_PUBLIC_URL", "").rstrip("/")
    bucket = os.getenv("R2_BUCKET_NAME")
    if not url.startswith(public_url):
        return
    key = url[len(public_url) + 1:]
    _client().delete_object(Bucket=bucket, Key=key)
