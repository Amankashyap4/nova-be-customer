import json
import os
import sys

import pinject
from dotenv import load_dotenv
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from loguru import logger

# Add "app" root to PYTHONPATH so we can import from app i.e. from app import create_app.
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)  # noqa

from app import APP_ROOT, create_app  # noqa: E402

# load .env file into system
dotenv_path = os.path.join(APP_ROOT, ".env")
load_dotenv(dotenv_path)

KAFKA_SUBSCRIPTIONS = os.getenv("KAFKA_SUBSCRIPTIONS")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_CONSUMER_GROUP_ID = os.getenv(
    "KAFKA_CONSUMER_GROUP_ID", default="CUSTOMER_CONSUMER_GROUP"
)
KAFKA_SERVER_AUTH_USERNAME = os.getenv("KAFKA_SERVER_AUTH_USERNAME")
KAFKA_SERVER_AUTH_PASSWORD = os.getenv("KAFKA_SERVER_AUTH_PASSWORD")
subscriptions = KAFKA_SUBSCRIPTIONS.split("|")
bootstrap_servers = KAFKA_BOOTSTRAP_SERVERS.split("|")

if __name__ == "__main__":
    logger.info("CONNECTING TO SERVER")
    try:
        consumer = KafkaConsumer(
            bootstrap_servers=bootstrap_servers,
            auto_offset_reset="earliest",
            group_id=KAFKA_CONSUMER_GROUP_ID,
            security_protocol="SASL_PLAINTEXT",
            sasl_mechanism="SCRAM-SHA-256",
            sasl_plain_username=KAFKA_SERVER_AUTH_USERNAME,
            sasl_plain_password=KAFKA_SERVER_AUTH_PASSWORD,
        )
    except KafkaError as exc:
        logger.error(f"Failed to consume message on Kafka broker with error {exc}")
    else:
        consumer.subscribe(subscriptions)
        logger.info(f"Event Subscription List: {subscriptions}")
        logger.info("AWAITING MESSAGES\n")

        app = create_app()
        app_ctx = app.app_context()
        app_ctx.push()

        # Application context should be registered before importing from app
        from app.controllers import CustomerController
        from app.events import EventSubscriptionHandler
        from app.repositories import CustomerRepository, RegistrationRepository
        from app.schema import CustomerSchema
        from app.services import AuthService, ObjectStorage, RedisService

        for msg in consumer:
            data = json.loads(msg.value)
            logger.info(f"originating service: {data.get('service_name')}")
            logger.info(f"topic consuming: {msg.topic}")
            obj_graph = pinject.new_object_graph(
                modules=None,
                classes=[
                    CustomerController,
                    CustomerRepository,
                    RedisService,
                    RegistrationRepository,
                    AuthService,
                    CustomerSchema,
                    ObjectStorage,
                ],
            )
            customer_controller = obj_graph.provide(CustomerController)
            event_subscription_handler = EventSubscriptionHandler(customer_controller)
            event_subscription_handler.event_handler(data)
            logger.info("message status: successfully consumed\n")
