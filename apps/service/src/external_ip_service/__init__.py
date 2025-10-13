from time import sleep, time

from loguru import logger
from redis import Redis

# from sys import stdout


def main() -> None:
    # logger.add(stdout, format="{time} [{level}] {message}", level="INFO")

    logger.info("Connecting redis server...")
    redis = Redis()

    logger.info("Start service")
    while True:
        try:
            redis.set("time", str(int(time())))
            logger.info("Time was updated")
            sleep(10)
        except KeyboardInterrupt:
            logger.info("Exit")
            return 0
