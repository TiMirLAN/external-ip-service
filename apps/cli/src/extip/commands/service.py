import asyncio
from pathlib import Path
from typing import Any

import click
from loguru import logger


class Service:
    def __init__(self, socket_path: Path) -> None:
        self.socket_path = socket_path

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

    async def run_periodic_update(self) -> None: ...

    async def run_iptables_watcher(self) -> None: ...

    async def run(self) -> None:
        await asyncio.gather(
            self.run_server(),
            self.run_periodic_update(),
            self.run_iptables_watcher(),
        )

    @classmethod
    def start(cls, socket_path: Path) -> None:
        try:
            service = cls(socket_path)
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
@click.pass_context
def service(ctx: dict[str | Any], log_level: str) -> None:
    """Start the service"""
    # logger.level(log_level)
    Service.start(socket_path=ctx.obj["SOCKET_PATH"])
