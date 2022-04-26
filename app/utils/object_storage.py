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


# response = s3_client.list_buckets()
#
# for bucket in response["Buckets"]:
#     print(bucket["Name"])
#
# response = s3_client.list_objects(Bucket="nova-bucket")
# b = response.Bucket("nova-bucket")
# print(response.get("Contents"))
# for bucket in b.objects.all():
#     print(bucket.key)


# try:
#     response = s3_client.generate_presigned_post(
#         Bucket="nova-bucket",
#         Key="sample",
#         ExpiresIn=60
#     )
# except ClientError:
#     raise AppException.OperationError(
#         context=f"error generating pre-signed url"
#     )
#
# print(response)
# #
# # with open("__init__.py", 'rb') as file:
#     # files = {'file': file}
# files = {'file': ('newfile', open("config.py", "r"))}
# ur = requests.post(response["url"], data=response["fields"], files=files)
#
# print(f"upload response: {ur.content}")
# #
# #
# response = s3_client.list_objects(Bucket="nova-bucket")
# b = response.Bucket("nova-bucket")
# print(response.get("Contents"))
# for o in response.get('Contents'):
# print(o.get("Key"))
# s3_client.delete_object(Bucket='nova-bucket', Key=o.get("Key"))
#     data = s3_client.get_object(Bucket="nova-bucket", Key=o.get('Key'))
#     contents = data['Body'].read()
#     print(contents.decode("utf-8"))


def upload_file(obj):
    if obj.profile_image:
        try:
            response = s3_client.generate_presigned_post(
                Bucket=Config.CEPH_BUCKET, Key=obj.profile_image, ExpiresIn=60
            )
        except ClientError:
            raise AppException.OperationError(context="error generating pre-signed url")
        obj.pre_signed_post = response
        return obj
    return None


def download_file(obj):
    if obj.profile_image:
        try:
            response = s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": Config.CEPH_BUCKET, "Key": obj.profile_image},
                ExpiresIn=60,
            )
        except ClientError:
            raise AppException.OperationError(context="error generating pre-signed url")
        obj.pre_signed_get = response
        return obj
    return None
