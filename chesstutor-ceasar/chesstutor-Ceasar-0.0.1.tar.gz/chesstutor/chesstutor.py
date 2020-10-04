import pdb
import random

import chess
import chess.engine
import click

engine = chess.engine.SimpleEngine.popen_uci('/usr/local/bin/stockfish')

@click.group()
def cli():
    pass

@click.command()
def play():
    """Play chess against an AI with an AI assisting you."""
    board = chess.Board()
    while not board.is_game_over():
        click.echo(board)
        legal_moves = []
        for legal_move in board.legal_moves:
            board.push(legal_move)
            info = engine.analyse(board, chess.engine.Limit(time=0.1))
            legal_moves.append((info["score"].relative.score(), legal_move))
            board.pop()
        legal_moves.sort(key=lambda score_move: score_move[0])
        best_moves = legal_moves[:3]
        random.shuffle(best_moves)
        click.echo("\nBest moves:")
        for score, move in best_moves:
            click.echo("- {}".format(move))
        command = input("Your move: ")
        move = chess.Move.from_uci(command)
        board.push(move)
        click.echo("\nScores:")
        for score, move in sorted(best_moves, key=lambda score_move: score_move[0]):
            click.echo("1. {} {}".format(move, -score))

        result = engine.play(board, chess.engine.Limit(time=0.5))
        click.echo("\nBlack plays: {}".format(result.move))
        board.push(result.move)

cli.add_command(play)

if __name__ == '__main__':
    cli()
