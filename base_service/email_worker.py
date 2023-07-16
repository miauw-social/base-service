from enum import StrEnum
import json
import aio_pika


class EmailTemplates(StrEnum):
    VERIFY = "sign_up"


class EMailWorker:
    def __init__(self, url: str):
        self.connection = None
        self.url: str = url
        self.channel: aio_pika.abc.AbstractChannel = None
        self.ex: aio_pika.abc.AbstractExchange = None

    async def setup(self, chan_id: int | None = None) -> "EMailWorker":
        """setup worker"""
        self.connection = await aio_pika.connect(self.url)
        self.channel = await self.connection.channel(channel_number=chan_id)
        self.ex = self.channel.default_exchange
        return self

    async def send(self, typ: EmailTemplates, recipient: str, subject: str, **context):
        await self.setup()
        await self.ex.publish(
            aio_pika.Message(
                json.dumps(
                    {
                        "type": typ,
                        "recipient": recipient,
                        "subject": subject,
                        "payload": context,
                    },
                ).encode("utf-8")
            ),
            routing_key="email",
        )
