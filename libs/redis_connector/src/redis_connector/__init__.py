from typing import Optional

from pydantic import BaseModel
from redis import Redis

__all__ = ["RedisConnector"]


class ApiIPInfoIOLiteMeResponse(BaseModel):
    ip: str
    asn: str
    as_name: str
    as_domain: str
    country: str
    continent_code: str
    continent: str


class ConnectorState(BaseModel):
    message: str
    ip_data: Optional[ApiIPInfoIOLiteMeResponse] = None


class RedisConnector:
    def __init__(self, redis_key: str = "external_ip_info") -> None:
        self.connection: Optional[Redis] = None
        self.key = redis_key

    def connect(self) -> None:
        self.connection = Redis()

    def setIpInfo(self, state: ConnectorState) -> None:
        self.connection.set(self.key, state.model_dump(mode="json"))

    def getIpInfo(self) -> ConnectorState:
        value = self.connection.get(self.key)
        if not value:
            return ConnectorState(message="No data found")
        return ConnectorState.model_validate_json(value)
