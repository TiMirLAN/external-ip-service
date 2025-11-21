from typing import Any, Optional

import click
from loguru import logger

from extip.services.server_service import Service


@click.command()
@click.option(
    "--log-level",
    "-l",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
)
@click.option(
    "--token",
    "-t",
    type=str,
    help="The 'ipinfo.com' access token.",
    envvar="EXTIP_TOKEN",
)
@click.pass_context
def service(ctx: dict[str | Any], log_level: str, token: Optional[str]) -> None:
    """Start the service"""
    # logger.level(log_level)
    logger.info("Starting service...")
    Service.start(socket_path=ctx.obj["SOCKET_PATH"], token=token)
