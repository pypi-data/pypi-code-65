import click

import chesstutor

@click.group()
def cli():
    pass

@click.command()
def play():
    """Play chess against an AI with an AI assisting you."""
    chesstutor.play()
    


cli.add_command(play)

if __name__ == '__main__':
    cli()
