
import ujson
import click
import re
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter
from tabulate import tabulate
import pandas as pd
from datetime import datetime


def success_response(msg):
    click.echo(click.style("\nSUCCESS 🎉\n", fg="green"))
    click.echo(msg.strip())


def to_table(data, tablefmt="psql", missingval="?",
             showindex=False, hide=[], showheaders=True):
    def tabulate_rename(string):
        dictionary = {
            "Regt": "RegT",
            "Sma": "SMA",
            "Pnl": "P&L",
            " Id": " ID",
            "True": "Yes ",
            "False": "No   ",
            "Ecn": "ECN",
            "Tuid": "TUID",
            "Tsid": "TSID",
            "Figi": "FIGI",
            "Sic": "SIC",
            "Mic": "MIC",
        }
        for k, v in dictionary.items():
            string = string.replace(k, v)

        return string.replace("IDentifiers", "Identifiers")

    def draw(values, headers, missingval, tablefmt, showindex, showheaders):
        if showheaders:
            return "\n" + tabulate_rename(tabulate(
                values, headers=headers,
                missingval=missingval, tablefmt=tablefmt, showindex=showindex))

        return "\n" + tabulate_rename(tabulate(
                values,
                missingval=missingval, tablefmt=tablefmt, showindex=showindex))

    if isinstance(data, dict):
        clean_data = {}
        for k, v in data.items():
            if k not in hide:
                clean_data[k] = v
        data = clean_data
        return draw(
            data.values(), headers=data.keys(),
            missingval=missingval, tablefmt=tablefmt,
            showindex=showindex, showheaders=showheaders
        )
    elif isinstance(data, pd.DataFrame):
        return draw(
            data, headers="keys",
            missingval=missingval, tablefmt=tablefmt,
            showindex=showindex, showheaders=showheaders
        )

    headers = []
    if isinstance(data, list):
        clean_data = []
        for item in data:
            tmp = {}
            for k, v in item.items():
                if k not in ["url"]:
                    tmp[k] = v
            clean_data.append(tmp)
        data = clean_data

        headers = data[0].keys()
        values = [item.values() for item in data if item not in hide]
    elif isinstance(data, dict):
        clean_data = {}
        for k, v in data.items():
            if k not in hide:
                clean_data[k] = v
        data = clean_data
        headers = data.keys()
        values = data.values()

    headers = [col.replace("_", " ").title() for col in headers]
    return draw(
            values, headers=headers,
            missingval=missingval, tablefmt=tablefmt,
            showindex=showindex, showheaders=showheaders
        )


def to_json(obj):
    json_str = ujson.dumps(obj, indent=4, sort_keys=True)
    return "\n" + highlight(
        json_str.replace("\/", "/"), JsonLexer(), TerminalFormatter()
    ).strip()


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class dictx(dict):
    def first(self, key, default=None):
        value = self.get(key)
        if not value:
            return default
        if isinstance(value, list) and len(value) > 0:
            return value[0]
        return value

    def last(self, key, default=None):
        value = self.get(key)
        if not value:
            return default
        if isinstance(value, list) and len(value) > 0:
            return value[-1]
        return value

    def nth(self, key, loc, default=None):
        value = self.get(key)
        if not value:
            return default
        if isinstance(value, list) and len(value) > loc:
            return value[loc]
        return value



def args_parser(args, required={}, optional={}, flags={}):
    args = " " + " ".join(args)
    flags["raw"] = ["--raw"]

    _flags = {}
    for key, flag_opt in flags.items():
        _flags[key] = []
        for flag in flag_opt:
            flag = f" {flag}"
            _flags[key].append(flag in args)
            args = args.replace(flag, "")
        _flags[key] = any(_flags[key])

    regex = []
    if required:
        for key, options in required.items():
            if len(options) > 1:
                args = args.replace(f' {options[0]} ', f' {options[1]} ')
                regex.append(options[1])
            regex.append(options[0])

    if optional:
        for key, options in optional.items():
            if len(options) > 1:
                args = args.replace(f' {options[0]} ', f' {options[1]} ')
                regex.append(options[1])
            regex.append(options[0])

    regex = "|".join(regex)
    pattern = f'(\s({regex})[=|\s]([:.a-zA-Z0-9_-]+))'
    pairs = re.findall(pattern, args, re.MULTILINE)

    options = {}
    for k, v in [pair[1:3] for pair in pairs]:
        options.setdefault(k.replace('-', ''), []).append(v)

    missing = []
    for item in required:
        if item not in options:
            missing.append(item)

    if missing:
        raise click.UsageError(
            "Missing required options: `--{missing}`".format(
                missing='`, `--'.join(missing)))

    for k, v in _flags.items():
        options[k] = v

    return dictx(options)


def parse_date(timestamp):
    timestamp = str(timestamp)

    if timestamp.isdigit():
        timestamp_int = int(timestamp)
        if len(timestamp) == 19:
            timestamp = datetime.utcfromtimestamp(timestamp_int / 1e9)
        elif len(timestamp) == 16:
            timestamp = datetime.utcfromtimestamp(timestamp_int / 1e6)
        elif len(timestamp) == 13:
            timestamp = datetime.utcfromtimestamp(timestamp_int / 1e3)
        else:
            timestamp = datetime.utcfromtimestamp(timestamp_int)
    else:
        try:
            timestamp = datetime.fromisoformat(timestamp)
        except ValueError:
            return None, None

    return timestamp.strftime(
        "%Y-%m-%d %H:%M:%S.%f").replace(" 00:00:00.000000", ""), timestamp
