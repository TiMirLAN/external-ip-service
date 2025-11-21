import asyncio
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import click
from loguru import logger

from extip.utils import (
    IpInfoClient,
    IpInfoClientError,
    IpInfoClientTimeout,
    SimpleIpInfo,
)


class Status(Enum):
    READY = "ready"
    ERROR = "error"
    UPDATING = "updating"


class Service:
    def __init__(self, socket_path: Path, token: Optional[str]) -> None:
        self.socket_path = socket_path
        self.ipinfo_client = IpInfoClient(token)
        self.status: Status = Status.UPDATING
        self.info: Optional[SimpleIpInfo] = None

    async def client_handler(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        logger.debug(f"Client connected: {reader.get_extra_info('peername')}")
        writer.write(r"debug")
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def run_server(self) -> None:
        logger.debug(f"Initializing server on {self.socket_path}")
        server = await asyncio.start_unix_server(
            self.client_handler,
            path=self.socket_path,
        )
        logger.info(f"Server started on {self.socket_path}")
        async with server:
            await server.serve_forever()

    async def run_periodic_update(self) -> None:
        while True:
            try:
                self.status = Status.UPDATING
                self.info = await self.ipinfo_client.fetch_simple_data()
                self.status = Status.READY
            except (IpInfoClientError, IpInfoClientTimeout):
                self.status = Status.ERROR

    async def run_iptables_watcher(self) -> None: ...

    async def run(self) -> None:
        await asyncio.gather(
            self.run_server(),
            self.run_periodic_update(),
            self.run_iptables_watcher(),
        )

    @classmethod
    def start(cls, socket_path: Path, token: str) -> None:
        try:
            service = cls(socket_path, token)
            asyncio.run(service.run())
        except KeyboardInterrupt:
            logger.info("Service stopped by keyboard interrupt")


@click.command()
@click.option(
    "--log-level",
    "-l",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
)
@click.option("--token", "-t", type=str, help="The 'ipinfo.com' access token.")
@click.pass_context
def service(ctx: dict[str | Any], log_level: str, token: Optional[str]) -> None:
    """Start the service"""
    # logger.level(log_level)
    Service.start(socket_path=ctx.obj["SOCKET_PATH"], token=token)
