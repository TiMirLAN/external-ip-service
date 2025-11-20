from pathlib import Path
import asyncio

import click
from loguru import logger


class Service:
    def __init__(self, socket_path: Path):
        self.socket_path = socket_path

    async def client_handler(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        logger.debug(f"Client connected: {reader.get_extra_info('peername')}")
        writer.write(r"debug")
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    async def run_server(self):
        logger.debug(f"Initializing server on {self.socket_path}")
        server = await asyncio.start_unix_server(
            self.client_handler,
            path=self.socket_path,
        )
        logger.info(f"Server started on {self.socket_path}")
        async with server:
            await server.serve_forever()

    async def run_periodic_update(self): ...

    async def run_iptables_watcher(self): ...

    async def run(self):
        await asyncio.gather(
            self.run_server(),
            self.run_periodic_update(),
            self.run_iptables_watcher(),
        )

    @classmethod
    def start(cls, socket_path: Path):
        try:
            service = cls(socket_path)
            asyncio.run(service.run())
        except KeyboardInterrupt as kbe:
            logger.info("Service stopped by keyboard interrupt")


@click.command()
@click.option(
    "--log-level",
    "-l",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
)
@click.pass_context
def service(ctx, log_level):
    """Start the service"""
    # logger.level(log_level)
    Service.start(socket_path=ctx.obj["SOCKET_PATH"])
