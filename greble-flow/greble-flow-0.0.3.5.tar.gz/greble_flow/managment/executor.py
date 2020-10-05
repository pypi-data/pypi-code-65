import click


@click.group()
def cli():
    pass


@cli.command()
@click.option("--port", prompt="Port", help="Port", default=5000)
@click.option("--debug", prompt="Debug", help="Debug", default=False)
def runprocessor(port: int, debug: bool):
    from greble_flow.web.managment import app

    app.run(port=port, debug=debug)
