"""Воркер: слушает очередь emails и «отправляет» письма (это КОНСЬЮМЕР).

Запускается как ОТДЕЛЬНЫЙ процесс, независимо от веб-приложения:
    python worker.py

Это и есть смысл брокера: веб-приложение только кладёт задачи в очередь,
а реальную работу (отправку писем) делает этот воркер. Его можно
останавливать, перезапускать и запускать в несколько копий — задачи из
очереди при этом не теряются.
"""
import json

import pika

from broker import EMAIL_QUEUE, RABBITMQ_URL


def handle_message(ch, method, properties, body):
    """Обработчик одного сообщения из очереди."""
    message = json.loads(body)
    # Здесь была бы реальная отправка письма (SMTP, SendGrid и т.п.).
    # Для учёбы просто печатаем — суть та же.
    print(
        f"[email] Отправляю письмо на {message['to']}: "
        f"«Добро пожаловать, {message['username']}!»"
    )
    # Подтверждаем обработку (ack). Без этого RabbitMQ снова отдаст сообщение.
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue=EMAIL_QUEUE, durable=True)

    # Не давать воркеру больше 1 задачи за раз, пока не подтвердит предыдущую.
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=EMAIL_QUEUE, on_message_callback=handle_message)

    print("Воркер запущен. Жду задачи из очереди. Ctrl+C для выхода.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nОстановка воркера.")
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
