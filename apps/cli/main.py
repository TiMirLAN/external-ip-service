#!/usr/bin/env python3
import click

from extip.commands.service import service
from extip.commands.client import client

ENV_VAR_PREFIX = "EXTIP"


@click.group()
@click.option(
    "--socket-path",
    "-s",
    default="/tmp/extip.sock",
    type=click.Path(),
    help="Path to the socket file for client connections",
)
@click.pass_context
def cli(ctx, socket_path):
    ctx.ensure_object(dict)
    ctx.obj["SOCKET_PATH"] = socket_path


def main():
    cli.add_command(service)
    cli.add_command(client)
    cli(auto_envvar_prefix=ENV_VAR_PREFIX)


if __name__ == "__main__":
    main()
