"""Kafka consumer module."""

import asyncio
import json
import logging
from typing import Any, AsyncGenerator, NoReturn

from kafka import KafkaConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

consumer = KafkaConsumer(
    "chat_topic",
    bootstrap_servers="kafka:9092",
    group_id="chat-group",
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="latest",
)


async def consume_messages_async() -> AsyncGenerator[Any, NoReturn]:
    """Consume messages from a Kafka topic asynchronously."""
    await asyncio.sleep(0.1)

    partitions = consumer.assignment()
    for partition in partitions:
        consumer.seek_to_end(partition)

    while True:
        for message in consumer:
            logger.info(f"Consumed message: {message.value}")
            yield message.value
