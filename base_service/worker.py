from typing import Callable, Awaitable, Any
import aio_pika
import json
import traceback
import os


class RabbitMQWorker:
    """RabbitMQ Base Worker Class"""

    def __init__(self, url: str):
        self.connection = None
        self.url: str = url
        self.channel: aio_pika.abc.AbstractChannel = None
        self.ex: aio_pika.abc.AbstractExchange = None

    async def setup(self, chan_id: int | None = None) -> "RabbitMQWorker":
        """setup worker"""
        self.connection = await aio_pika.connect(self.url)
        self.channel = await self.connection.channel(channel_number=chan_id)
        self.ex = self.channel.default_exchange
        return self

    async def send(self, queue_name: str, data: dict | str | bytes) -> None:
        """sends something to queue"""
        try:
            data = json.dumps(data).encode("utf-8")
        except json.JSONDecodeError:
            data = data.encode("utf-8")
        await self.ex.publish(aio_pika.Message(data), routing_key=queue_name)

    async def listen(
        self,
        queue_name: str,
        worker_function: Callable[[Any], Awaitable[Any]]
    ):
        await self.setup()
        queue = await self.channel.declare_queue(queue_name)
        async with queue.iterator() as qi:
            message: aio_pika.abc.AbstractMessage
            async for message in qi:
                try:
                    async with message.process(requeue=False):
                        assert message.reply_to is not None
                        try:
                            data = json.loads(message.body)
                        except json.JSONDecodeError:
                            data = message.body.decode("utf-8")
                        res = await worker_function(data)
                        await self.ex.publish(
                            aio_pika.Message(
                                body=json.dumps(res).encode("utf-8"),
                                correlation_id=message.correlation_id,
                            ),
                            routing_key=message.reply_to,
                        )
                except Exception as e:
                    if isinstance(e, AssertionError):
                        try:
                            data = json.loads(message.body)
                        except json.JSONDecodeError:
                            data = message.body.decode("utf-8")
                        await worker_function(data)
                    else:
                        print("[!] Exception: ", e)
                        if os.getenv("SERVICE_TRACEBACK") == "active":
                            print(traceback.format_exc())
