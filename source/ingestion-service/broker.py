import aio_pika
from aio_pika import ExchangeType
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

host = "localhost"
port = 5672
user = "guest"
password = "guest"

_connection = None
_channel = None
_exchange = None


async def init_rabbitmq():
    global _connection, _channel, _exchange

    _connection = await aio_pika.connect_robust(
        host=host,
        port=port,
        login=user,
        password=password
    )

    _channel = await _connection.channel()

    _exchange = await _channel.declare_exchange(
        "sensor_events",
        ExchangeType.DIRECT,
        durable=True,
    )
    queue = await _channel.declare_queue(
        "normalized_events",
        durable=True
    )

    await queue.bind(
        _exchange,
        routing_key="normalized.sensor"
    )


async def publish_message(routing_key: str, body: bytes):
    await _exchange.publish(
        aio_pika.Message(
            body=body,
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        ),
        routing_key=routing_key,
    )


async def close_rabbitmq():
    global _connection
    if _connection is not None:
        await _connection.close()