"""RabbitMQ: publishing tasks to a queue (this is the PRODUCER).

We use pika — a synchronous RabbitMQ client. Publishing is fast, so it is
fine to call it from a regular (sync) endpoint.
"""
import json
import logging

import pika

from config import settings

RABBITMQ_URL = settings.RABBITMQ_URL
EMAIL_QUEUE = "emails"  # queue we drop "send email" tasks into

logger = logging.getLogger(__name__)


def publish_email(message: dict) -> None:
    """Drop a "send email" task into the queue.

    We open a new connection per publish — simple and robust for a learning
    project. Real apps reuse the connection, since opening one each time is costly.
    """
    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        try:
            channel = connection.channel()
            # durable=True -> the queue survives a RabbitMQ restart
            channel.queue_declare(queue=EMAIL_QUEUE, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=EMAIL_QUEUE,
                body=json.dumps(message),
                # delivery_mode=2 -> the message itself is persisted to disk too
                properties=pika.BasicProperties(delivery_mode=2),
            )
            logger.info("Task published to queue %s: %s", EMAIL_QUEUE, message)
        finally:
            connection.close()
    except Exception as exc:
        # Broker unavailable? Don't fail registration because of it — just log.
        # (In production this would be a transactional outbox or retries.)
        logger.warning("Failed to publish task to RabbitMQ: %s", exc)


def get_email_publisher():
    """FastAPI dependency. Overridden in tests with a list append (no RabbitMQ)."""
    return publish_email
