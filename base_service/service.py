from base_service import RabbitMQWorker
from collections import defaultdict
import asyncio
import typing
import logging


class BaseService:
    """creates the base service class"""

    def __init__(
        self, name: str, url: str, logfile: str = None, worker_log: bool = True
    ):
        self.worker = RabbitMQWorker(url)
        self.events: list[str] = []
        self.m: dict[
            str, typing.Callable[[typing.Any], typing.Awaitable[typing.Any]]
        ] = defaultdict()
        self.name = name
        # logging
        self.logger = logging.getLogger(name)
        self.log_formatter = logging.Formatter("[%(asctime)s] - %(name)s - %(message)s")
        self.log_filehandler = logging.FileHandler(logfile or "service.log")
        self.log_streamhandler = logging.StreamHandler()
        self.logger.setLevel(logging.DEBUG)
        self.log_filehandler.setLevel(logging.DEBUG)
        self.log_streamhandler.setLevel(logging.INFO)
        self.log_filehandler.setFormatter(self.log_formatter)
        self.log_streamhandler.setFormatter(self.log_formatter)
        self.logger.addHandler(self.log_filehandler)
        self.logger.addHandler(self.log_streamhandler)

    def start(self):
        """starts the service"""
        self.logger.info("starting")
        loop = asyncio.get_event_loop()
        for ev in self.events:
            self.logger.info(f"listening for event '{ev}'")
        loop.run_until_complete(
            asyncio.gather(*[self.worker.listen(k, v) for k, v in self.m.items()])
        )

    def event(self, event: str):
        """adds a new event handler for event"""

        def wrapper(handler: typing.Callable[[dict], typing.Awaitable[dict]]):
            self.logger.debug(f"add handler {handler} for event '{event}'")
            self.events.append(event)
            self.m[event] = handler

        return wrapper
