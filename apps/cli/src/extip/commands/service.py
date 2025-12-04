import sys
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
    logger.remove()
    # Send DEBUG, INFO, WARNING to stdout
    logger.add(
        sys.stdout,
        level=log_level,
        filter=lambda record: record["level"].name in ["DEBUG", "INFO", "WARNING"],
    )
    # Send ERROR, CRITICAL to stderr
    logger.add(
        sys.stderr,
        level="ERROR",
        filter=lambda record: record["level"].name in ["ERROR", "CRITICAL"],
    )
    logger.info("Starting service...")
    Service.start(socket_path=ctx.obj["SOCKET_PATH"], token=token, logger=logger)
