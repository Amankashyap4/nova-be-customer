import inspect

import boto3
from botocore.client import Config as boto_config
from botocore.exceptions import ClientError, ConnectionError

from app.core.exceptions import AppException
from app.utils import get_full_class_name, message_struct
from config import Config

boto3_config = boto_config(connect_timeout=3, retries={"max_attempts": 0})

s3_client = boto3.client(
    "s3",
    aws_access_key_id=Config.CEPH_ACCESS_KEY,
    aws_secret_access_key=Config.CEPH_SECRET_KEY,
    endpoint_url=Config.CEPH_SERVER_URL,
    config=boto3_config,
)


def set_object(obj):
    if obj.profile_image not in [None, "null"]:
        try:
            response = s3_client.generate_presigned_post(
                Bucket=Config.CEPH_BUCKET, Key=obj.profile_image, ExpiresIn=300
            )
        except ClientError as exc:
            raise AppException.OperationError(
                context="error generating pre-signed url",
                error_message=message_struct(
                    exc_class=get_full_class_name(exc),
                    module=__name__,
                    method=inspect.currentframe().f_code.co_name,
                    calling_module=inspect.stack()[1],
                    calling_method=inspect.currentframe().f_back.f_code.co_name,
                    error=exc,
                ),
            )
        except ConnectionError as exc:
            raise AppException.OperationError(
                context="error connecting to object storage server",
                error_message=message_struct(
                    exc_class=get_full_class_name(exc),
                    module=__name__,
                    method=inspect.currentframe().f_code.co_name,
                    calling_module=inspect.stack()[1],
                    calling_method=inspect.currentframe().f_back.f_code.co_name,
                    error=exc,
                ),
            )
        obj.pre_signed_post = response
    return obj


def download_object(obj):
    if obj.profile_image not in [None, "null"]:
        try:
            response = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": Config.CEPH_BUCKET, "Key": obj.profile_image},
                ExpiresIn=300,
            )
        except ClientError as exc:
            raise AppException.OperationError(
                context="error generating pre-signed url",
                error_message=message_struct(
                    exc_class=get_full_class_name(exc),
                    module=__name__,
                    method=inspect.currentframe().f_code.co_name,
                    calling_module=inspect.stack()[1],
                    calling_method=inspect.currentframe().f_back.f_code.co_name,
                    error=exc,
                ),
            )
        except ConnectionError as exc:
            raise AppException.OperationError(
                context="error connecting to object storage server",
                error_message=message_struct(
                    exc_class=get_full_class_name(exc),
                    module=__name__,
                    method=inspect.currentframe().f_code.co_name,
                    calling_module=inspect.stack()[1],
                    calling_method=inspect.currentframe().f_back.f_code.co_name,
                    error=exc,
                ),
            )
        obj.pre_signed_get = response
    return obj


def unset_object(obj):
    try:
        s3_client.delete_object(Bucket="nova-bucket", Key=obj.profile_image)
    except ClientError as exc:
        raise AppException.OperationError(
            context="error generating pre-signed url",
            error_message=message_struct(
                exc_class=get_full_class_name(exc),
                module=__name__,
                method=inspect.currentframe().f_code.co_name,
                calling_module=inspect.stack()[1],
                calling_method=inspect.currentframe().f_back.f_code.co_name,
                error=exc,
            ),
        )
    except ConnectionError as exc:
        raise AppException.OperationError(
            context="error connecting to object storage server",
            error_message=message_struct(
                exc_class=get_full_class_name(exc),
                module=__name__,
                method=inspect.currentframe().f_code.co_name,
                calling_module=inspect.stack()[1],
                calling_method=inspect.currentframe().f_back.f_code.co_name,
                error=exc,
            ),
        )
    return obj


def saved_objects(key=None):
    images = []
    try:
        response = s3_client.list_objects(Bucket="nova-bucket")
    except ClientError as exc:
        raise AppException.OperationError(
            context="error generating pre-signed url",
            error_message=message_struct(
                exc_class=get_full_class_name(exc),
                module=__name__,
                method=inspect.currentframe().f_code.co_name,
                calling_module=inspect.stack()[1],
                calling_method=inspect.currentframe().f_back.f_code.co_name,
                error=exc,
            ),
        )
    except ConnectionError as exc:
        raise AppException.NotFoundException(
            context="error connecting to object storage server",
            error_message=message_struct(
                exc_class=get_full_class_name(exc),
                module=__name__,
                method=inspect.currentframe().f_code.co_name,
                calling_module=inspect.stack()[1],
                calling_method=inspect.currentframe().f_back.f_code.co_name,
                error=exc,
            ),
        )
    if response.get("Contents"):
        for obj in response.get("Contents"):
            if not key:
                images.append(obj)
            elif key and key in obj.values():
                return obj
    return images
