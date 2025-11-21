from dataclasses import dataclass

from httpx import AsyncClient


@dataclass
class SimpleIpInfo:
    ip: str
    asn: str
    as_name: str
    as_domain: str
    country_code: str
    country: str
    continent_code: str
    continent: str


class IpInfoClient:
    def __init__(self, token: str) -> None:
        self.client = AsyncClient()
        self.params = dict(token=token)

    async def fetch_simple_data(self) -> SimpleIpInfo:
        async with self.client:
            response = await self.client.get(
                "https://api.ipinfo.io/lite/me", params=self.params
            )
            ip_data: dict[str, str] = response.json()
            return SimpleIpInfo(**ip_data)
