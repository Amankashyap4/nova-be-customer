import boto3
from botocore.exceptions import ClientError

from app.core.exceptions import AppException
from config import Config

s3_client = boto3.client(
    "s3",
    aws_access_key_id=Config.CEPH_ACCESS_KEY,
    aws_secret_access_key=Config.CEPH_SECRET_KEY,
    endpoint_url=Config.CEPH_SERVER_URL,
)


def object_upload_url(obj):
    if obj.profile_image and obj.profile_image != "null":
        try:
            response = s3_client.generate_presigned_post(
                Bucket=Config.CEPH_BUCKET, Key=obj.profile_image, ExpiresIn=300
            )
        except ClientError as exc:
            raise AppException.OperationError(
                context="error generating pre-signed url",
                error_message={"object_upload_url": exc},
            )
        obj.pre_signed_post = response
        return obj
    return None


def object_download_url(obj):
    if obj.profile_image and obj.profile_image != "null":
        try:
            response = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": Config.CEPH_BUCKET, "Key": obj.profile_image},
                ExpiresIn=300,
            )
        except ClientError as exc:
            raise AppException.OperationError(
                context="error generating pre-signed url",
                error_message={"object_download_url": exc},
            )
        obj.pre_signed_get = response
        return obj
    return None
