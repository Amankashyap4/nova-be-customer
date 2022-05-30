import json
import os

from kafka import KafkaProducer
from kafka.errors import KafkaError
from loguru import logger

from app.core.exceptions import AppException

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", default="localhost:90")
bootstrap_servers = KAFKA_BOOTSTRAP_SERVERS.split("|")


def json_serializer(data):
    return json.dumps(data).encode("UTF-8")


def get_partition(key, all, available):
    """

    :param key, all, available:
    :return:
    """
    return 0


def publish_to_kafka(topic, value):
    try:
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=json_serializer,
            partitioner=get_partition,
        )
        producer.send(topic=topic, value=value)
        return True
    except KafkaError as exc:
        logger.error(f"Failed to publish record on to Kafka broker with error {exc}")
        raise AppException.OperationError(context=f"kafka error with error {exc}")
