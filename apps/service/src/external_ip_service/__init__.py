from time import sleep

from loguru import logger
from redis_connector import RedisConnector


def main() -> None:
    logger.info("Connecting redis server...")
    connector = RedisConnector()
    connector.connect()

    logger.info("Start service")
    while True:
        try:
            ip_info = dict(ip="0.0.0.0")
            connector.setIpInfo(ip_info)
            logger.info(f"IP {ip_info['ip']} was updated")
            sleep(10)
        except KeyboardInterrupt:
            logger.info("Exit by keyboard interrupt")
            return 0
