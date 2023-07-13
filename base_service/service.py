from base_service import RabbitMQWorker
from collections import defaultdict
import asyncio
import typing
import inspect

class Service:
    """creates the base service class"""
    def __init__(self, url: str):
        self.worker = RabbitMQWorker(url)
        self.events: list[str] = []
        self.m: dict[str, typing.Callable[[dict], typing.Awaitable[dict]]] = defaultdict()

    def start(self):
        """starts the service"""
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(*[self.worker.listen(k,v) for k,v in self.m.items()]))


    def add_event_handler(self, event: str, handler: typing.Callable[[dict], typing.Awaitable[dict]]) -> None:
        """adds a new event handler for service"""
        self.events.append(event)
        self.m[event] = handler
