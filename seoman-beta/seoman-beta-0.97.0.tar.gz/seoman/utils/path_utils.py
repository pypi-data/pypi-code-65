from pathlib import Path
from typing import List
import typer


def create_toml_list() -> List[str]:
    """Go to folder"""
    path = Path(Path.home() / ".queries").glob("*.toml")
    files = [file for file in path if file.is_file()]

    # Files comes like PosixPath("/some/path.toml") we are converting it to just filename without extension
    files = [str(file).split("/")[-1].split(".")[0] for file in files]

    if len(files) >= 1:
        return files

    typer.secho("0 query found, add some.", bold=True, fg=typer.colors.BRIGHT_RED)
    exit()

