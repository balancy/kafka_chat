"""Kafka producer module."""

import json
import logging

from kafka import KafkaProducer
from kafka.errors import KafkaError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)


def publish_message(topic: str, message: dict) -> None:
    """Publish a message to a Kafka topic."""
    try:
        producer.send(topic, value=message)
        producer.flush()
        logger.info(f"Published message: {message}")
    except KafkaError:
        logger.exception("Failed to publish message")
