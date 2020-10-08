from datupie.core.startproject import StartCommand
from datupie.core.deployproject import DeployCommand
from datupie.core.destroyproject import DestroyCommand

FUNCTION_MAP = {
    'startproject': StartCommand().startproject,
    'deployproject': DeployCommand().deployproject,
    'destroyproject': DestroyCommand().destroyproject
}