from hashlib import sha256
from http.client import HTTPConnection
from json import loads
from socket import timeout
from subprocess import check_output
from time import sleep, time

from loguru import logger
from redis_connector import RedisConnector

ROUTES_TIMEOUT = 3
IP_REQUEST_TIMEOUT = 5
IP_CHECK_TIMEOUT = 60


def build_routes_hash() -> str:
    output = check_output("ip route show", shell=True, text=True)
    return sha256(output.encode()).hexdigest()


def get_external_ip_data() -> dict:
    attempts = 0
    while True:
        logger.info(
            f"Updating ip...{' attempt' + str(attempts) if attempts > 0 else ''}"
        )
        try:
            connection = HTTPConnection("ipinfo.io", timeout=IP_REQUEST_TIMEOUT)
            connection.request("GET", "/json")
            response = connection.getresponse()
            data = response.read()
            return loads(data)
        except timeout:
            attempts += 1
        except Exception:
            logger.error("\nError updating ip")


def update_ip_info(connector: RedisConnector) -> None:
    ip_info = get_external_ip_data()
    logger.info(f"New ip info: {ip_info['ip']} {ip_info['region']} {ip_info['org']}")
    connector.setIpInfo(ip_info)


def main() -> None:
    logger.info("Connecting redis server...")
    connector = RedisConnector()
    connector.connect()

    logger.info("Start service")

    routes_hash = build_routes_hash()
    connector.setIpInfo(get_external_ip_data())
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
                update_ip_info(connector)
                last_update_time = time()
            else:
                if time() - last_update_time > IP_CHECK_TIMEOUT:
                    update_ip_info(connector)
                    last_update_time = time()
            sleep(ROUTES_TIMEOUT)
        except KeyboardInterrupt:
            logger.info("Exit by keyboard interrupt")
            return 0
