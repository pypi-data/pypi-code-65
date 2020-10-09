from datetime import datetime, timedelta
from logging import getLogger
from pathlib import Path

from invoicez.cli import command, dir_path_option
from invoicez.paths import Paths


_logger = getLogger(__name__)


@command
@dir_path_option
def new(dir_path: str) -> None:
    """Create a new invoice."""
    paths = Paths(Path(dir_path))
    now = datetime.now()
    prefix = now.strftime("%Y-%m")
    date = now.strftime("%d/%m/%Y")
    limit_date = (now + timedelta(days=31)).strftime("%d/%m/%Y")
    n = len(list(paths.git_dir.glob(f"*/{prefix}-*.yml"))) + 1
    output_path = paths.working_dir / f"{prefix}-{n:03}.yml"
    content = paths.template_invoice.read_text(encoding="utf8")
    content = content.replace("{DATE}", date)
    content = content.replace("{LIMIT_DATE}", limit_date)
    _logger.info(
        f"Copying invoice template to {output_path.relative_to(paths.working_dir)}"
    )
    output_path.write_text(content, encoding="utf8")
