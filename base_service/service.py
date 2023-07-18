from base_service.email_worker import EMailWorker
from base_service.worker import RabbitMQWorker
from base_service.utils import run_async
from psycopg_pool import AsyncConnectionPool
import asyncio
import typing
import logging
import os


class BaseService:
    """creates the base service class"""

    def __init__(
            self, name: str, rabbitmq_url: str | None = os.getenv("RABBITMQ_URL"),
            postgres_url: str | None = os.getenv("POSTGRES_URL"), logfile: str = None, worker_log: bool = True
    ):
        if not rabbitmq_url:
            raise Exception("No URL provided and env var 'RABBITMQ_URL' is empty.")
        if postgres_url:
            self.postgres_url = postgres_url
        else:
            self.postgres_url = None
        self.worker = RabbitMQWorker(rabbitmq_url)
        self.emailer = EMailWorker(rabbitmq_url)
        self.events: list[str] = []
        self.m: dict[
            str, dict[typing.Callable[[typing.Any], typing.Awaitable[typing.Any]]]
        ] = dict(rpc={}, basic={})
        self.name = name
        self._pool: AsyncConnectionPool | None = None
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
        # run init db
        if postgres_url:
            run_async(self.init_db())

    def start(self):
        """starts the service"""
        self.logger.info("starting")
        loop = asyncio.get_event_loop()
        for ev in self.events:
            self.logger.info(f"listening for event '{ev}'")
        loop.run_until_complete(
            asyncio.gather(
                *[self.worker.listen(event, handler) for a in self.m.values() for event, handler in a.items()])
        )

    async def init_db(self,
                      prepare_statements: bool = True,
                      path: str = "./sql/",
                      include_sub_dirs: bool = True,
                      exclude_files: list[str] = [],
                      min_size: int = 5,
                      max_size: int = 15):
        """initialises the connection with the database and prepares the statements."""
        self.__setattr__("_pool", AsyncConnectionPool(self.postgres_url, min_size=5, max_size=15))

    @property
    def pool(self):
        """returns the database connection pool of the service"""
        return self._pool

    def event(self, event: str, event_type: str = "rpc"):
        """adds a new event handler for event"""

        def wrapper(handler: typing.Callable[[dict], typing.Awaitable[dict]]):
            self.logger.debug(f"add handler {handler} for event '{event}'")
            self.events.append(event)
            self.m[event_type][event] = handler

        return wrapper
