from hashlib import sha256
from http.client import HTTPConnection
from socket import timeout
from subprocess import check_output
from time import sleep, time

from loguru import logger
from redis_connector import ApiIPInfoIOLiteMeResponse, ConnectorState, RedisConnector

from .settings import settings

ROUTES_TIMEOUT = 3
IP_REQUEST_TIMEOUT = 5
IP_CHECK_TIMEOUT = 60


def build_routes_hash() -> str:
    output = check_output("ip route show", shell=True, text=True)
    return sha256(output.encode()).hexdigest()


def fetch_external_ip_data(connector: RedisConnector) -> dict:
    attempts = 0
    while True:
        attempts += 1
        logger.info(
            f"Updating ip...{' attempt ' + str(attempts) if attempts > 0 else ''}"
        )
        try:
            connector.setIpInfo(ConnectorState(message=f"[{attempts}] Updating..."))
            connection = HTTPConnection("api.ipinfo.io", timeout=IP_REQUEST_TIMEOUT)
            connection.request("GET", f"/lite/me?token={settings.ipinfo_token}")
            response = connection.getresponse()
            data = response.read()
            ip_data = ApiIPInfoIOLiteMeResponse.model_validate_json(data)
            logger.info(
                f"New ip info: {ip_data.ip} {ip_data.country} {ip_data.as_name}"
            )
            connector.setIpInfo(ConnectorState(message="Fetched!", ip_data=ip_data))
            return
        except timeout:
            logger.warning("Request timeout")
        except Exception:
            connector.setIpInfo(ConnectorState(message="Error!"))
            logger.error("\nError updating ip")


def main() -> None:
    logger.info("Connecting redis server...")
    connector = RedisConnector()
    connector.connect()

    logger.info("Start service")

    routes_hash = build_routes_hash()
    fetch_external_ip_data(connector)
    last_update_time = time()

    while True:
        try:
            # if time() - last_update_time < ROUTES_TIMEOUT:
            #     continue
            # last_update_time = time()
            new_route_hash = build_routes_hash()

            if new_route_hash != routes_hash:
                routes_hash = new_route_hash
                logger.info("Route table changed. Updating IP info....")
                fetch_external_ip_data(connector)
                last_update_time = time()
            else:
                if time() - last_update_time > IP_CHECK_TIMEOUT:
                    fetch_external_ip_data(connector)
                    last_update_time = time()
            sleep(ROUTES_TIMEOUT)
        except KeyboardInterrupt:
            connector.setIpInfo(ConnectorState(message="Service is down"))
            logger.info("Exit by keyboard interrupt")
            return 0
