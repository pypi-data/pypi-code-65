from pathlib import Path
from typing import Any, List

from click import argument, Path as ClickPath

from invoicez.cli import command, dir_path_option, option
from invoicez.paths import Paths
from invoicez.runner import run as runner_run


def _autocomplete_path(ctx: Any, args: List[str], incomplete: str) -> List[str]:
    try:
        paths = Paths(Path("."))
        return [
            str(t.relative_to(paths.working_dir))
            for t in paths.working_dir.glob("*.yml")
            if t.name != "company-config.yml"
        ]
    except Exception:
        return []


def _autocomplete_template(ctx: Any, args: List[str], incomplete: str) -> List[str]:
    try:
        paths = Paths(Path("."))
        return [
            t.with_suffix("").with_suffix("").name
            for t in paths.jinja2_dir.glob("*.tex.jinja2")
        ]
    except Exception:
        return []


@command
@argument(
    "path",
    type=ClickPath(exists=True, dir_okay=False, readable=True),
    autocompletion=_autocomplete_path,  # type: ignore
)
@option(
    "--template",
    type=str,
    default="main",
    autocompletion=_autocomplete_template,  # type: ignore
)
@dir_path_option
def run(path: str, template: str, dir_path: str) -> None:
    """Run the compiler."""
    paths = Paths(Path(dir_path))
    runner_run(Path(path), template, paths)
