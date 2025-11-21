from sys import stdout

from redis_connector import ApiIPInfoIOLiteMeResponse, RedisConnector


def main() -> None:
    connector = RedisConnector()
    connector.connect()
    ip_info = connector.getIpInfo()
    if ip_info.ip_data is None:
        stdout.write(ip_info.message)
    else:
        ipd: ApiIPInfoIOLiteMeResponse = ip_info.ip_data
        stdout.write(f"{ipd.ip} {ipd.country} {ipd.as_name}")
