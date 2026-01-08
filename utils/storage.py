import os
import uuid
import shutil
from fastapi import UploadFile
import boto3

BASE_UPLOAD_DIR = "uploads/bonds"


def save_locally(upload_file: UploadFile) -> str:
    os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)

    ext = upload_file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(BASE_UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(upload_file.file, f)

    # return URL-style path (important)
    return f"/uploads/bonds/{filename}"


def upload_to_cloud(upload_file: UploadFile) -> str:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name=os.getenv("AWS_REGION")
    )

    key = f"bonds/{uuid.uuid4()}-{upload_file.filename}"

    s3.upload_fileobj(
        upload_file.file,
        os.getenv("S3_BUCKET"),
        key,
        ExtraArgs={"ContentType": upload_file.content_type}
    )

    return f"https://{os.getenv('S3_BUCKET')}.s3.amazonaws.com/{key}"


def store_file(upload_file: UploadFile) -> str:
    """
    Single entry point.
    Switch storage without touching service code.
    """
    if os.getenv("ENV") == "production":
        return upload_to_cloud(upload_file)
    return save_locally(upload_file)
