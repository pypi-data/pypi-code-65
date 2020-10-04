import click

import chesstutor

@click.command()
def play():
    """Play chess against an AI with an AI assisting you."""
    chesstutor.play()

if __name__ == '__main__':
    play()
