"""RabbitMQ: публикация задач в очередь (это ПРОДЮСЕР).

Используем pika — синхронный клиент RabbitMQ. Публикация быстрая,
поэтому её спокойно можно звать из обычного (sync) эндпоинта.
"""
import json
import logging

import pika

from config import settings

RABBITMQ_URL = settings.RABBITMQ_URL
EMAIL_QUEUE = "emails"  # имя очереди, куда кладём задачи на отправку писем

logger = logging.getLogger(__name__)


def publish_email(message: dict) -> None:
    """Кладёт задачу «отправить письмо» в очередь.

    На каждую публикацию открываем новое соединение — это просто и надёжно
    для учебного проекта. В реальном проекте соединение переиспользуют,
    т.к. открывать его каждый раз дорого.
    """
    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        try:
            channel = connection.channel()
            # durable=True -> очередь переживёт перезапуск RabbitMQ
            channel.queue_declare(queue=EMAIL_QUEUE, durable=True)
            channel.basic_publish(
                exchange="",
                routing_key=EMAIL_QUEUE,
                body=json.dumps(message),
                # delivery_mode=2 -> само сообщение тоже сохраняется на диск
                properties=pika.BasicProperties(delivery_mode=2),
            )
            logger.info("Задача отправлена в очередь %s: %s", EMAIL_QUEUE, message)
        finally:
            connection.close()
    except Exception as exc:
        # Брокер недоступен? Регистрацию из-за этого НЕ валим — просто логируем.
        # (В проде тут был бы transactional outbox или ретраи.)
        logger.warning("Не удалось опубликовать задачу в RabbitMQ: %s", exc)


def get_email_publisher():
    """Зависимость FastAPI. В тестах подменяется на запись в список (без RabbitMQ)."""
    return publish_email
