import logging
from typing import List, Optional
import sys

from minionize import minionizer, ProcessCallback
from minionize.reporter import create_reporter

import pandas as pd
import time

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


SPACE = " "


class Section:
    def __init__(
        self, content: str, title: Optional[str] = None, caption: str = "", sep="-"
    ):
        self.title = title
        self.content = content
        self.sep = sep
        self.caption = caption

    def __str__(self) -> str:
        s = ""
        if self.title is not None:
            s += self.title
            s += "\n"
            s += self.sep * len(self.title)
            s += "\n"
        s += self.content
        s += "\n"
        s += self.caption
        return s


def _pad(left: str, right: str, margin: str) -> str:
    """This create two columns left content padded."""
    left_lines = left.splitlines()
    padding = max([len(l) for l in left_lines] + [0])
    right_lines = right.splitlines()
    max_lines = max(len(left_lines), len(right_lines))
    left_lines.extend([""] * (max_lines - len(left_lines)))
    right_lines.extend([""] * (max_lines - len(right_lines)))
    result = []
    for l, r in zip(left_lines, right_lines):
        result.append(l.ljust(padding, SPACE) + margin + r)
    return "\n".join(result)


class Row:
    def __init__(
        self, sections: List[Section], title: Optional[str] = None, margin: int = 8
    ):
        self.title = title
        self.margin = margin
        self._margin = SPACE * margin
        self.sections = sections
        self.title = title

    def __str__(self) -> str:
        s = ""
        if self.title is not None:
            s += self.title
            s += "\n"
            s += "=" * len(self.title)
            s += "\n"

        if self.sections == []:
            return s
        str_sections = str(self.sections[0])
        for section in self.sections[1:]:
            str_sections = _pad(str_sections, str(section), self._margin)
        s += str_sections + "\n\n"
        return s


def _ascii_chart(df: pd.DataFrame, COLS: int):
    # we want two columns with some margins
    # but this shouldn't exceed COLS
    from asciichartpy import plot, blue, green, lightmagenta, colored

    margin = 3
    columns = (COLS / 2) - margin
    line = []
    derivative1 = [0]
    derivative10 = [0] * 10
    start = df.start.min()
    end = df.end.max()
    step = max(0.1, round((end - start) / columns, 1))
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
    # mean rate
    mean = [len(df) / (df.end.max() - df.start.min())] * len(derivative1)

    left = Section(
        plot(line, {"height": 10}), title=f"Number of generation [{step}s step)]"
    )

    config = dict(height=10, colors=[lightmagenta, blue, green])
    right = Section(
        plot([mean, derivative1, derivative10], config),
        title=f"Generation rate (/s) ",
        caption=f"{colored('mean rate', lightmagenta)} \nsliding windows of {colored('1*step', blue)}, {colored('10*step', green)}",
    )
    print(Row([left, right]))


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

    title = f"Processing time (first={start.strftime(format)} last={end.strftime(format)} duration={end-start})"
    s1 = Section(df.process.describe().to_string(), title="Process time summary")
    s2 = Section(
        df.groupby(pd.cut(df.process, bins=10, precision=1))
        .count()
        .process.to_string(),
        title="Process time distribution",
    )
    by_error = df.groupby("error").count().process
    content = by_error.to_string()
    if by_error.empty:
        content = "No processing error detected."

    s3 = Section(content, title="Processing errors")
    print(Row([s1, s2, s3], title=title))


def _resources(df):
    nodes = df.nodename.unique()
    extra_title = ""
    if "oar_job_id" in df:
        oar_job_ids = df.oar_job_id.unique()
        extra_title = f" / {len(oar_job_ids)} jobs"

    by = []
    if "oar_job_id" in df:
        by.append("oar_job_id")
    by.append("nodename")
    # since last mean process time
    duration = round(df.process.mean(), 0)
    last = (
        df[df.end > (time.time() - duration)].groupby(by=by).genation.count().nlargest()
    )

    # print some columns
    left = Section(
        df.groupby(by=by).genation.count().nlargest().to_string(),
        title="Most active (all time)",
    )
    if last.empty:
        content = "No data."
    else:
        content = last.to_string()

    right = Section(content, title=f"Most active (last {duration}s)")

    print(Row([left, right], title=f"Resources ({len(nodes)} nodes {extra_title})"))


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
    _resources(df)
