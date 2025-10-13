from sys import stdout

from redis_connector import RedisConnector


def main() -> None:
    connector = RedisConnector()
    connector.connect()
    ip_info = connector.getIpInfo()
    stdout.write(f"{ip_info['ip']}")
