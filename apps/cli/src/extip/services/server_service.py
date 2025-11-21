import asyncio
from enum import Enum
from pathlib import Path
from typing import Optional

from loguru import logger
from pydantic import BaseModel

from extip.services.iptables import IptablesService
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


class ServiceState(BaseModel):
    status: Status
    info: SimpleIpInfo


class Service:
    def __init__(self, socket_path: Path, token: Optional[str]) -> None:
        self.socket_path = socket_path
        self.ipinfo_client = IpInfoClient(token)
        self.status: Status = Status.UPDATING
        self.info: Optional[SimpleIpInfo] = None
        self.updating_timeout = 5.0
        self.iptables = IptablesService()
        self.iptables_timeout = 2.0

    @property
    def state(self) -> ServiceState:
        return ServiceState(status=self.status, info=self.info)

    @property
    def state_dict(self) -> dict[str, str | dict[str, str]]:
        return self.state.model_dump()

    @property
    def state_json(self) -> str:
        return self.state.model_dump_json()

    async def client_handler(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        logger.debug("Client connected")
        writer.write(self.state_json.encode())
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

    async def update_ip_info(self) -> None:
        try:
            logger.debug("Updating ip...")
            self.status = Status.UPDATING
            self.info = await self.ipinfo_client.fetch_simple_data()
            self.status = Status.READY
            logger.debug(f"IP fetched {self.info.ip} {self.info.as_domain}")
        except (IpInfoClientError, IpInfoClientTimeout) as e:
            self.status = Status.ERROR
            logger.error(f"Error '{e}' fetching ip...")

    async def run_periodic_update(self) -> None:
        while True:
            await self.update_ip_info()
            await asyncio.sleep(self.updating_timeout)

    async def run_iptables_watcher(self) -> None:
        while True:
            if self.iptables.check_table_changed():
                logger.info("Iptables changed")
                await self.update_ip_info()
            await asyncio.sleep(self.iptables_timeout)

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
