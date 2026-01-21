from __future__ import annotations

import json
import time
import aio_pika

from app.metrics import BROKER_PUBLISH_TOTAL, BROKER_PUBLISH_DURATION_SECONDS


async def publish_event(
    *,
    rmq_url: str,
    exchange_name: str,
    routing_key: str,
    payload: dict,
) -> None:

    started = time.time()
    try:
        connection = await aio_pika.connect_robust(rmq_url)
        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                exchange_name,
                aio_pika.ExchangeType.TOPIC,
                durable=True,
            )
            message = aio_pika.Message(
                body=json.dumps(payload).encode("utf-8"),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )
            await exchange.publish(message, routing_key=routing_key)

        BROKER_PUBLISH_TOTAL.labels(result="ok").inc()
    except Exception:
        BROKER_PUBLISH_TOTAL.labels(result="error").inc()
        raise
    finally:
        BROKER_PUBLISH_DURATION_SECONDS.observe(time.time() - started)


async def publish_order_created(
    *,
    rmq_url: str,
    exchange_name: str,
    routing_key: str,
    order_id: int,
) -> None:
    await publish_event(
        rmq_url=rmq_url,
        exchange_name=exchange_name,
        routing_key=routing_key,
        payload={"order_id": order_id},
    )
