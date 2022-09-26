import os

import boto3
import requests
from botocore.client import Config as boto_config
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from app.core.extensions import db
from app.services.redis_service import redis_conn
from config import Config


def redis_available():
    redis_conn.client()
    return True, "redis is ok"


def postgres_available():
    try:
        result = db.engine.execute("SELECT 1")
        if result:
            return True, "database is ok"
    except Exception as e:
        return False, str(e)


def keycloak_available():
    try:
        response = requests.get(
            url=Config.KEYCLOAK_URI + "/auth/realms/" + Config.KEYCLOAK_REALM
        )
    except requests.exceptions.RequestException as e:
        return False, str(e)
    if response.status_code == 200:
        return True, "keycloak is ok"
    else:
        return False, "keycloak is not ok"


def ceph_available():
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=Config.CEPH_ACCESS_KEY,
        aws_secret_access_key=Config.CEPH_SECRET_KEY,
        endpoint_url=Config.CEPH_SERVER_URL,
        config=boto_config(retries={"max_attempts": 3}),
    )
    response = s3_client.head_bucket(Bucket=Config.CEPH_BUCKET).get("ResponseMetadata")

    if response.get("HTTPStatusCode") == 200:
        return True, "ceph server is ok"
    else:
        return False, "ceph server is not ok"


def kafka_available():
    try:
        KafkaConsumer(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS").split("|"),
            auto_offset_reset="earliest",
            group_id="CUSTOMER_CONSUMER_GROUP,",
            security_protocol="SASL_PLAINTEXT",
            sasl_mechanism="SCRAM-SHA-256",
            sasl_plain_username=os.getenv("KAFKA_SERVER_AUTH_USERNAME"),
            sasl_plain_password=os.getenv("KAFKA_SERVER_AUTH_PASSWORD"),
        )
    except KafkaError as exc:
        return False, str(exc)
    return True, "kafka is ok"


HEALTH_CHECKS = [
    redis_available,
    postgres_available,
    ceph_available,
    keycloak_available,
    kafka_available,
]
