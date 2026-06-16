"""Worker: listens to the emails queue and "sends" emails (this is the CONSUMER).

Runs as a SEPARATE process, independent of the web app:
    python worker.py

This is the whole point of a broker: the web app only drops tasks into the
queue, and the real work (sending emails) is done by this worker. It can be
stopped, restarted, and run in several copies — tasks in the queue are not lost.
"""
import json

import pika

from broker import EMAIL_QUEUE, RABBITMQ_URL


def handle_message(ch, method, properties, body):
    """Handle a single message from the queue."""
    message = json.loads(body)
    # A real email send would go here (SMTP, SendGrid, etc.).
    # For learning we just print it — the idea is the same.
    print(
        f"[email] Sending email to {message['to']}: "
        f"\"Welcome, {message['username']}!\""
    )
    # Acknowledge processing (ack). Without it, RabbitMQ would redeliver the message.
    ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue=EMAIL_QUEUE, durable=True)

    # Don't give the worker more than 1 task at a time until it acks the previous one.
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=EMAIL_QUEUE, on_message_callback=handle_message)

    print("Worker started. Waiting for tasks from the queue. Ctrl+C to exit.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("\nStopping worker.")
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
