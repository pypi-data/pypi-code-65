import click

from grid import Grid
from grid.utilities import is_experiment


@click.command()
@click.argument('runs_or_experiments', type=str, required=True, nargs=-1)
def cancel(runs_or_experiments: str) -> None:
    """Cancels running runs or experiments"""
    client = Grid()

    if len(runs_or_experiments) == 0:
        raise click.BadArgumentUsage("""
        Pass in Runs or Experiments, for instance:

        grid cancel run_1 run_2
        grid cancel run_1-exp1 run_2

        """)

    #  TODO: allow cancelling all at once or make async so that each
    #  cancel call doesn't block the next.
    for run_or_exp in runs_or_experiments:
        #  Cancel Experiment
        if is_experiment(run_or_exp):
            client.cancel(experiment_id=run_or_exp)

        #  Cancel Run
        else:
            client.cancel(run_id=run_or_exp)
