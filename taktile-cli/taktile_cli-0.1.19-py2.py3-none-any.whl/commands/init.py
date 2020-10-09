from typing import Optional

from tktl.core.loggers import CliLogger
from tktl.core.managers.project import ProjectManager

logger = CliLogger()


def init_project(path: Optional[str], name: str):
    project_path = ProjectManager.init_project(path, name)
    logger.log(
        f"Project scaffolding created successfully at {project_path}", color="green",
    )
