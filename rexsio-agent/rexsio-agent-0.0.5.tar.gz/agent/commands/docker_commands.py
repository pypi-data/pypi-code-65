from agent.commands import logger
from agent.commands.shell_executor import execute_shell_command
from agent.exceptions.agent_error import AgentError


def docker_compose_pull(path):
    execute_shell_command(f'docker-compose -f {path} pull')


def docker_compose_up(path):
    execute_shell_command(f'docker-compose -f {path} up -d')


def docker_compose_down(path):
    execute_shell_command(f'docker-compose -f {path} down')


def docker_compose_restart(path):
    try:
        execute_shell_command(f'docker-compose -f {path} restart')
    except AgentError:
        logger.exception(f'Failed to restart docker-compose {path}')
        docker_compose_up(path)
