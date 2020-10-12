from datetime import datetime
import logging
from typing import List, Optional
import re
import sys

from minionize import minionizer, ProcessCallback
from minionize.reporter import create_reporter

from asciichartpy import plot, blue, green, lightmagenta, colored, white
import humanize
import pandas as pd
import time

logging.basicConfig(level=logging.DEBUG)


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

    def get_width(self):
        title_lines = [""]
        if self.title is not None:
            title_lines = self.title.splitlines()
        content_lines = self.content.splitlines()
        caption_lines = ""
        if self.caption is not None:
            caption_lines = self.caption.splitlines()
        lines = []
        lines.extend(title_lines)
        lines.extend(content_lines)
        lines.extend(caption_lines)
        return max([len(l) for l in lines])


def escape_ansi(line: str) -> str:
    """remove any ansi caracter from a string.

    e.g colors
    """
    ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", str(line))


def _pad(left: str, right: str, margin: str) -> str:
    """This create two columns left content padded."""
    left_lines = left.splitlines()
    padding = max([len(escape_ansi(l)) for l in left_lines] + [0])
    right_lines = right.splitlines()
    max_lines = max(len(left_lines), len(right_lines))
    left_lines.extend([""] * (max_lines - len(left_lines)))
    right_lines.extend([""] * (max_lines - len(right_lines)))
    result = []
    for l, r in zip(left_lines, right_lines):
        l_without_ansi = escape_ansi(l)
        pad = max(padding - len(l_without_ansi), 0)
        fill = SPACE * pad
        result.append(l + fill + margin + r)
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
            s += "\n\n"

        if self.sections == []:
            return s
        str_sections = str(self.sections[0])
        for section in self.sections[1:]:
            str_sections = _pad(str_sections, str(section), self._margin)
        s += str_sections + "\n\n"
        return s


def _graph_cumulative_number(df: pd.DataFrame, columns: int = 30) -> Section:
    """Gives an estimation of the number of elements.

    Number of elements means elements that have finished(terminated) before a
    given point of time.

    Args:
        df: A dataframe.
            Must contains the columns start, end
            One line per element to count
        columns: the number of columns to use in the terminal to display the
            graph

    Returns:
        A section containing the graph
    """
    # we want two columns with some margins
    # but this shouldn't exceed COLS
    title = f"Rate (/s) "
    if df.empty:
        return Section("No data.", title)
    # will hold the number of terminated generations
    line = []
    derivative1 = [0]
    derivative10 = [0] * 10
    start = df.start.min()
    end = df.end.max()
    # step depends on the column width
    step = max(0.1, round((end - start) / columns, 1))
    current = df.start.min()
    while current < df.end.max() + step:
        # how many finished before this point (cumsum)
        count_items = len(df[df.end < current])
        line.append(count_items)
        if len(line) > 1:
            derivative1.append((line[-1] - line[-2]) / step)
        if len(line) > 10:
            derivative10.append((line[-1] - line[-11]) / (10 * step))
        current += step

    # mean rate
    mean_rate = len(df) / (df.end.max() - df.start.min())
    mean_rate_line = [mean_rate] * len(derivative1)

    # common config for the plots
    # we increase a bit the default because we'll likely 100 000+ generations
    # and 1 million is maybe not that unlikely neither
    config = dict(height=10, format="{:10.2f} ", colors=[lightmagenta, blue, green])
    return Section(
        plot([mean_rate_line, derivative1, derivative10], config),
        title=title,
        caption=f"{colored('Mean rate', lightmagenta)}: {round(mean_rate, 2)} \nSliding windows of {colored('1*step', blue)}, {colored('10*step', green)}",
    )


def _graph_inflight_number(df: pd.DataFrame, columns: int = 30) -> Section:
    """Gives an estimation of the "inflight" elements.

    Inflight means element that have started but not finished at a given time.
    For instance the number of minions, or the number of generation that are
    currently being handled.
    Note that the latest estimation is *by design* wrong due to how we log
    events but will be eventually accurate (eventual accuracy).

    Args:
        df: A dataframe.
            Must contains the columns start, end
            One line per element to count
        columns: the number of columns to use in the terminal to display the
            graph

    Returns:
        A section containing the graph
    """
    # we want two columns with some margins
    # but this shouldn't exceed COLS

    title = f"Number"
    if df.empty:
        return Section("No data.", title)
    # will hold the number of terminated generations
    line = []
    line10 = [0] * 9
    start = df.start.min()
    end = df.end.max()
    # step depends on the column width
    step = max(0.1, round((end - start) / columns, 1))
    current = df.start.min()
    while current < df.end.max() + step:
        # how many finished before this point (inflight)
        count_items = len(df[(df["start"] <= current) & (df["end"] >= current)])
        line.append(count_items)
        if len(line) >= 10:
            line10.append(sum(line[-10:]) / 10.0)
        current += step

    config = dict(height=10, format="{:10.2f} ", colors=[white, green])
    return Section(
        plot([line, line10], config),
        title=title,
        caption=f"Current (max={round(max(line), 2)})\nSliding windows of {colored('10*step', green)}",
    )


def _stats_section(df: pd.DataFrame, key: str = "process_duration"):
    if df.empty:
        return Section("No data.", title="distribution (0 samples)")
    else:
        # intent: ensure the number of bins is between 1 and 10
        bins = min(max(int(df[key].max() - df[key].min()), 1), 10)
        content = (
            df.groupby(pd.cut(df[key], bins=bins, precision=1))
            .count()
            .rename(columns={key: "count"})[["count"]]
            .to_string()
        )
        return Section(
            content,
            title=f"distribution ({len(df)} samples)",
        )


def generation_stats(df: pd.DataFrame) -> Section:
    return _stats_section(df)


def success_stats(df: pd.DataFrame) -> Section:
    df_success = df[~df.error.notna()]
    return _stats_section(df_success)


def error_stats(df: pd.DataFrame) -> Section:
    df_error = df[df.error.notna()]
    return _stats_section(df_error)


def generation_section(df: pd.DataFrame, columns: int = 50) -> Section:
    return _graph_cumulative_number(df, columns=columns)


def generation_inflight_section(df: pd.DataFrame, columns: int = 50) -> Section:
    return _graph_inflight_number(df, columns=columns)


def success_section(df: pd.DataFrame, columns: int = 50) -> Section:
    # filter only success
    df_success = df[~df.error.notna()]
    return _graph_cumulative_number(df_success, columns=columns)


def error_section(df: pd.DataFrame, columns: int = 50) -> Section:
    # filter only error
    df_error = df[df.error.notna()]
    return _graph_cumulative_number(df_error, columns=columns)


def generations_all_time(df: pd.DataFrame) -> Section:
    by = ["nodename"]
    title = f"#generations (all time)"
    if "oar_job_id" in df:
        by.append("oar_job_id")
    most_active = df.groupby(by=by).count()["generation"].nlargest()
    if most_active.empty:
        content = "No data."
    else:
        content = most_active.to_string()
    return Section(content, title=title)


def generations_last_active(df: pd.DataFrame) -> Section:
    # compute an estimation of the last active windows
    window = 2 * df["process_duration"].mean()
    last_active = df[df["end"] >= time.time() - window]
    section = generations_all_time(last_active)
    section.title = f"#generations (last {round(window, 2)}s)"
    return section


def errors_all_time(df: pd.DataFrame) -> Section:
    errors = df[df["error"].notna()]
    section = generations_all_time(errors)
    section.title = f"#errors (all time)"
    return section


def errors_last_active(df: pd.DataFrame) -> Section:
    window = 2 * df["process_duration"].mean()
    last_active = df[df["end"] >= time.time() - window]
    errors = last_active[last_active["error"].notna()]
    section = generations_all_time(errors)
    section.title = f"#errors (last {round(window, 2)}s)"
    return section


def get_minion_df(df):
    minion_df = (
        df.groupby("uid")
        .agg(
            start=("start", "min"),
            end=("end", "max"),
            generation=("generation", "count"),
        )
        .reset_index()
    )
    minion_df["lifetime"] = minion_df["end"] - minion_df["start"]
    return minion_df


def minions_stats(df: pd.DataFrame, columns: int = 50) -> Section:
    minion_df = get_minion_df(df)
    s1 = _stats_section(minion_df, key="lifetime")
    s2 = _stats_section(minion_df, key="generation")
    return [
        s1,
        s2,
        _graph_inflight_number(
            minion_df, columns=columns - s1.get_width() - s2.get_width()
        ),
    ]


def summary(df: pd.DataFrame) -> Section:
    from inspect import cleandoc

    start = datetime.fromtimestamp(df["start"].min())
    end = datetime.fromtimestamp(df["end"].max())
    now = datetime.fromtimestamp(time.time())
    success = len(df[~df["error"].notna()])
    error_rate = 1 - success / len(df)
    success_rate_arrival = success / (end - start).seconds
    duration = end - start
    minions = len(df["uid"].unique())
    avg_per_minions = len(df) / minions
    minion_df = get_minion_df(df)

    content = f"""
    The timespan of the run is currently {humanize.precisedelta(duration)}.
    The start was observed {humanize.naturalday(start)}({humanize.naturaltime(now - start)}).

    {len(df)} generations has been spawned. This number can be decomposed in two parts:
    - {success} generations have been successfuly treated. This corresponds
      to the number of parameters for which a result has been produced.
    - {len(df) - success} error have been detected
    Doing the maths, approximately {round(error_rate, 2)}% of the generations failed.

    Results arrived at the mean rate of {round(success_rate_arrival, 2)} per second.

    Until now, {minions} minions have been spawned. In average your minions
    managed {round(avg_per_minions, 2)} generations. The oldest minion is
    aged of {humanize.naturaldelta(minion_df["lifetime"].max())}. The longest
    streak of parameters handled by one of your minions is
    {minion_df["generation"].max()}.

    Note that the above numbers may vary if the experiment is currently running.

    -=That's all for now.=-

    Cheers.
    """
    section = Section(cleandoc(content))
    return section


def status():
    """Read the reporter backend and get some stats out of it."""
    reporter = create_reporter()
    df = reporter.to_pandas()
    if df.empty:
        print(f"{reporter} reports no stat")
        return

    def extract_process(atomic_actions):
        return [
            a["end"] - a["start"] for a in atomic_actions if a["name"] == "process"
        ][0]

    df["process_duration"] = df.atomic_actions.apply(extract_process)

    print(banner())
    columns = 100

    s = error_stats(df)
    row = Row(
        [s, error_section(df, columns=columns - s.get_width())],
        title="Failures",
    )
    print(row)

    s = generation_stats(df)
    row = Row(
        [
            s,
            generation_section(df, columns=columns - s.get_width()),
        ],
        title="Generations (Succes + Failures)",
    )
    print(row)

    row = Row(
        [
            Section(SPACE * s.get_width()),
            generation_inflight_section(df, columns=columns - s.get_width()),
        ],
        title="Generations (Inflight)",
    )
    print(row)

    s = success_stats(df)
    row = Row(
        [s, success_section(df, columns=columns - s.get_width())],
        title="Success",
    )
    print(row)

    row = Row(
        [
            generations_all_time(df),
            generations_last_active(df),
            errors_all_time(df),
            errors_last_active(df),
        ],
        title="Generation activity (nlargest)",
    )
    print(row)

    row = Row([*minions_stats(df, columns=columns)], title="Your minions")
    print(row)

    row = Row([summary(df)], title="Summary")
    print(row)
