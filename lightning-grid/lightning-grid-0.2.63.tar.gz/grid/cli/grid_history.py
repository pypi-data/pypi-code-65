import click

from grid import Grid
from grid.types import ObservableType


@click.command()
@click.argument('observables', type=str, nargs=-1)
def history(observables: str) -> None:
    """
    View run and experiment history
    """
    client = Grid()

    if len(observables) == 0:
        kind = ObservableType.RUN
        _observables = []
    else:
        #  TODO: Provide support for multiple observables
        #  in a single command.
        _observables = observables[0].split('.')

        if len(_observables) == 1:
            kind = ObservableType.EXPERIMENT
        elif len(_observables) == 2:
            kind = ObservableType.EXPERIMENT
        else:
            raise click.BadArgumentUsage(
                'The observable passed does not work. ' +
                'Use the following format instead: ' +
                ' grid status RUN.EXPERIMENT ')

    client.history(kind=kind, identifiers=_observables)
