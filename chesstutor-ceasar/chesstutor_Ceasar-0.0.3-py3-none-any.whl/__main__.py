import click

@click.group()
def cli():
    pass

click.command()(play)

cli.add_command(play)

if __name__ == '__main__':
    cli()
