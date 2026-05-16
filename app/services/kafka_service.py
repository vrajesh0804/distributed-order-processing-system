"""
Kafka producer service.

Kafka is used to publish order_created events so background workers can process
inventory and payment asynchronously.
"""

import json
from kafka import KafkaProducer

from app.core.config import settings


def get_kafka_producer() -> KafkaProducer:
    """Create a Kafka producer that serializes Python dicts into JSON bytes."""
    return KafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )


def publish_order_created_event(event_data: dict) -> None:
    """Publish an order_created event to Kafka."""
    producer = get_kafka_producer()
    producer.send(settings.ORDER_CREATED_TOPIC, event_data)
    producer.flush()
    producer.close()
