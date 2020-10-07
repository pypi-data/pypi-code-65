import logging
import sys

from minionize import minionizer, ProcessCallback
from minionize.reporter import create_reporter

import pandas as pd

logging.basicConfig(level=logging.INFO)


def run():
    class _Callback(ProcessCallback):
        """Simplest callback

        Takes param as a string and append them to the original command.
        """

        def to_cmd(self, param):
            return " ".join(sys.argv[1:]) + " " + str(param)

    callback = _Callback()
    m = minionizer(callback)
    m.run()


# flake8: noqa: W605
def banner():
    return """
  __  __ _       _                   _        _
 |  \/  (_)     (_)                 | |      | |
 | \  / |_ _ __  _  ___  _ __    ___| |_ __ _| |_ ___
 | |\/| | | '_ \| |/ _ \| '_ \  / __| __/ _` | __/ __|
 | |  | | | | | | | (_) | | | | \__ \ || (_| | |_\__ \\
 |_|  |_|_|_| |_|_|\___/|_| |_| |___/\__\__,_|\__|___/

"""


def print_title(title: str):
    print(title)
    print("=" * len(title))


def _ascii_chart(df: pd.DataFrame, COLS: int):
    # sample every X min
    line = []
    derivative1 = [0]
    derivative10 = [0] * 10
    start = df.start.min()
    end = df.end.max()
    step = max(0.1, round((end - start) / COLS, 1))
    current = df.start.min()
    while current < df.end.max() + step:
        # how many finished before this point
        gen_before = len(df[df.end < current])
        line.append(gen_before)
        if len(line) > 1:
            derivative1.append((line[-1] - line[-2]) / step)
        if len(line) > 10:
            derivative10.append((line[-1] - line[-11]) / (10 * step))
        current += step
    from asciichartpy import plot, blue, green, colored

    print_title(f"Number of generation [{step}s step)]")
    print(plot(line, {"height": 10}))
    print("\n")

    print_title(
        f"Generation rate (/s) [sliding windows of {colored('1*step', blue)}, {colored('10*step', green)}]"
    )
    config = dict(height=10, colors=[blue, green])
    print(plot([derivative1, derivative10], config))
    print("\n")


def _stats(df: pd.DataFrame):
    # extract process time
    def extract_process(atomic_actions):
        return [
            a["end"] - a["start"] for a in atomic_actions if a["name"] == "process"
        ][0]

    from datetime import datetime

    format = "%Y-%m-%d %H:%M:%S"
    start = datetime.fromtimestamp(df.start.min())
    end = datetime.fromtimestamp(df.end.max())

    df["process"] = df.atomic_actions.apply(extract_process)
    title = f"Process time (first={start.strftime(format)} last={end.strftime(format)} duration={end-start})"
    print(title)
    print("=" * len(title))
    print(df.process.describe())
    print("\n")


def status():
    """Read the reporter backend and get some stats out of it."""
    COLS = 100
    reporter = create_reporter()
    df = reporter.to_pandas()
    if df.empty:
        print(f"{reporter} reports no stat")
        return
    nb_generation = len(df)
    rate_last = nb_generation / (df.end.max() - df.start.min())
    print(banner())
    _stats(df)
    _ascii_chart(df, COLS)
