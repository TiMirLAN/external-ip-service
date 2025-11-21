import click


@click.command()
def client() -> None:
    """Start the client"""
    click.echo("Starting the client...")
