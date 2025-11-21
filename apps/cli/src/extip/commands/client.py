import asyncio
from dataclasses import asdict
from pathlib import Path
from typing import Any

import click
from py_template_engine import TemplateEngine
from pydantic.dataclasses import dataclass
from pydantic_core import from_json

from extip.utils import SimpleIpInfo


@dataclass
class State:
    status: str
    info: SimpleIpInfo


async def fetch_info(socket_path: str | Path) -> State:
    (reader, *_) = await asyncio.open_unix_connection(path=socket_path)
    data = await reader.read()
    return State(**from_json(data))


@click.command()
@click.pass_context
@click.option("--info-format", "-i", default="{{status}} {{info.ip}}")
def client(ctx: dict[str | Any], info_format: str) -> None:
    """Start the client"""
    state = asyncio.run(fetch_info(socket_path=ctx.obj["SOCKET_PATH"]))
    click.echo(TemplateEngine(template_string=info_format).render(**asdict(state)))
