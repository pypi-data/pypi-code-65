import os
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable, TextIO, Tuple

import click
import pandas as pd  # type: ignore
from pandas import DataFrame  # type: ignore

# Avoid pandas truncation of the commands description
pd.set_option("display.max_colwidth", None)


def parse_dataframe_by_class_and_level(dataframe: DataFrame, buffer: TextIO) -> Iterable[Tuple[str, DataFrame]]:
    """Iterate dataframe over Java classes and command level"""
    for classname, cdf in dataframe.groupby("class"):
        # Write the class name as a section title and drop the column
        header = f"<h3>{classname}</h3>\n"
        cdf = cdf.drop(columns='class')

        if 'level' in cdf.columns:
            for level, ldf in cdf.groupby("level"):
                # Write the level name as a section title and drop the column
                header_full = header + f"<h5>{level}</h5>\n"
                ldf = ldf.drop(columns='level')
                yield header_full, ldf
        else:
            yield header, cdf


def clean_column(df: DataFrame, column_name: str) -> DataFrame:
    """Replace NaNs with empty string or remove column if full of NaNs"""
    if column_name in df.columns:
        if df[column_name].isna().all():
            df = df.drop(columns=column_name)
        else:
            df = df.fillna("")

    return df


def convert_dataframe(dataframe: DataFrame, output: Path) -> None:
    """Convert a pandas DataFrame to another table format"""
    file_format = output.suffix[1:]
    try:
        # Create temporary file to store HTML table
        tmpfile_ref, tmpfile_path = tempfile.mkstemp(text=True)
        with open(tmpfile_ref, "w") as buffer:
            for header, df in parse_dataframe_by_class_and_level(dataframe, buffer):
                print(header, file=buffer)
                df = clean_column(df, 'arguments')
                df = clean_column(df, 'description')
                df.sort_values('name', inplace=True)
                df.to_html(buf=buffer, index=False)
        # Use pandoc to convert from HTML to DOCX
        cmd = f"pandoc --from=html --to={file_format} -o {output} {tmpfile_path}"
        print(cmd)
        subprocess.check_call(cmd, shell=True)
    finally:
        # Remove temp file
        os.remove(tmpfile_path)

    print(f"{output} created.")


def select_and_convert(df: DataFrame, csv_file: Path, ext: str, cmd_type=None) -> None:
    if cmd_type is not None:
        df = _select_cmd_type(df, cmd_type)

    suffix = f".{ext}" if cmd_type is None else f"_{cmd_type.lower()}.{ext}"
    output = csv_file.with_name(csv_file.stem + suffix)

    convert_dataframe(df, output)


def _select_cmd_type(df: DataFrame, cmd_type: str) -> DataFrame:
    """Select a specific type of commands"""
    df = df.query(f"type == '{cmd_type.upper()}'")
    df = df.drop(columns="type")

    return df


@click.command("convert")
@click.argument("csv_file", type=click.Path(exists=True))
@click.option(
    "--to",
    "extension",
    type=str,
    default="docx",
    show_default=True,
    help="Output file extension.",
)
@click.option("--sort", is_flag=True, help="Orders commands alphabetically.")
@click.option("--split", is_flag=True, help="Splits the output into actions and queries.")
def main(csv_file, extension, split, sort):
    input_file = Path(csv_file)

    df_cmd: DataFrame = pd.read_csv(input_file)

    if split and 'level' in df_cmd.columns:
        select_and_convert(df_cmd, input_file, extension, cmd_type='action')
        select_and_convert(df_cmd, input_file, extension, cmd_type='query')
    else:
        select_and_convert(df_cmd, input_file, extension)
