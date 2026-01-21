import asyncio
import json
import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from app.settings import settings
from app.db import create_engine_and_sessionmaker
from app.worker import process_order, mark_failed


async def run() -> None:
    engine, SessionLocal = create_engine_and_sessionmaker(settings.db_dsn)

    connection = await aio_pika.connect_robust(settings.rmq_url)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=settings.prefetch_count)

        exchange = await channel.declare_exchange(
            settings.rmq_exchange,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )

        queue = await channel.declare_queue(settings.rmq_queue, durable=True)
        await queue.bind(exchange, routing_key=settings.rmq_routing_key_created)

        print(
            f"[consumer] listening queue='{settings.rmq_queue}' "
            f"exchange='{settings.rmq_exchange}' routing_key='{settings.rmq_routing_key_created}'"
        )

        async def on_message(message: AbstractIncomingMessage) -> None:
            async with message.process(requeue=False):
                payload = json.loads(message.body.decode("utf-8"))
                order_id = int(payload["order_id"])

                db = SessionLocal()
                try:
                    process_order(db, order_id)
                    db.commit()
                    print(f"[consumer] processed order_id={order_id}")
                except Exception as e:
                    db.rollback()
                    try:
                        mark_failed(db, order_id, f"{type(e).__name__}: {e}")
                        db.commit()
                    except Exception:
                        db.rollback()
                    print(f"[consumer] failed order_id={order_id}: {type(e).__name__}: {e}")
                    raise
                finally:
                    db.close()

        await queue.consume(on_message)

        await asyncio.Future()

    engine.dispose()


if __name__ == "__main__":
    asyncio.run(run())
