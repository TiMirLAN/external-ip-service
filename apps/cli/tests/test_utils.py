from types import TracebackType

import pytest

from extip.utils import IpInfoClient, SimpleIpInfo


def test_simple_ip_info_initialization() -> None:
    data = {
        "ip": "203.0.113.10",
        "asn": "AS12345",
        "as_name": "Example Networks",
        "as_domain": "example.net",
        "country_code": "US",
        "country": "United States",
        "continent_code": "NA",
        "continent": "North America",
    }

    info = SimpleIpInfo(**data)

    for key, value in data.items():
        assert value == getattr(info, key)


class MockResponse:
    def __init__(self, payload: dict[str, str]) -> None:
        self._payload = payload

    def json(self) -> dict[str, str]:
        return self._payload


class MockAsyncClient:
    def __init__(self, payload: dict[str, str]) -> None:
        self._payload = payload
        self.requests: list[tuple[str, dict[str, str]]] = []

    async def __aenter__(self) -> "MockAsyncClient":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None

    async def get(self, url: str, params: dict[str, str]) -> MockResponse:
        self.requests.append((url, params))
        return MockResponse(self._payload)


@pytest.mark.asyncio
async def test_ip_info_client_fetch_simple_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {
        "ip": "198.51.100.7",
        "asn": "AS54321",
        "as_name": "Demo ISP",
        "as_domain": "demo.isp",
        "country_code": "DE",
        "country": "Germany",
        "continent_code": "EU",
        "continent": "Europe",
    }
    mock_client = MockAsyncClient(payload)

    def fake_async_client() -> MockAsyncClient:
        return mock_client

    monkeypatch.setattr("extip.utils.AsyncClient", fake_async_client)

    client = IpInfoClient(token="secret-token")

    result = await client.fetch_simple_data()

    assert result == SimpleIpInfo(**payload)
    assert mock_client.requests == [
        ("https://api.ipinfo.io/lite/me", {"token": "secret-token"})
    ]
