from json import dumps, loads
from typing import Optional, Union

from redis import Redis

__all__ = ["RedisConnector"]

IPInfo = Union[object, str]


class RedisConnector:
    def __init__(self, redis_key: str = "external_ip_info") -> None:
        self.connection: Optional[Redis] = None
        self.key = redis_key

    def connect(self) -> None:
        self.connection = Redis()

    def setIpInfo(self, ip_information: Optional[IPInfo]) -> None:
        self.connection.set(self.key, dumps(ip_information))

    def getIpInfo(self) -> Optional[IPInfo]:
        value = self.connection.get(self.key)
        if not value:
            return None
        return loads(value)
