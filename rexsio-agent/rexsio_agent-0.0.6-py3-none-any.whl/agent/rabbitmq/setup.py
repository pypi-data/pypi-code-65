# TODO: https://gitlab.com/bettersolutions/issues-dac/rexs.io/-/issues/279
try:
    from importlib.resources import path
except ImportError:
    from importlib_resources import path

from agent.commands.docker_commands import docker_compose_up, docker_compose_pull
from agent.constants import DOCKER_COMPOSE_FILE


def setup_rabbitmq():
    with path("agent.rabbitmq.rabbit_docker_compose", f"{DOCKER_COMPOSE_FILE}") as docker_compose_path:
        docker_compose_pull(path=docker_compose_path)
        docker_compose_up(path=docker_compose_path)
