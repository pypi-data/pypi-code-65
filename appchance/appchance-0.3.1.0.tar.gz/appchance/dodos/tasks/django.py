from doit.action import CmdAction
from doit.tools import Interactive

dcc_params = [
    {"name": "compose_cmd", "short": "compose_cmd", "long": "compose_cmd", "type": str, "default": "docker-compose"},
    {"name": "dj_service", "short": "dj_service", "long": "dj_service", "type": str, "default": "django"},
]


def task_up():
    """ Start local docker containers. """

    def dcc(compose_cmd, dj_service):
        return f"{compose_cmd} up"

    return {"actions": [Interactive(dcc)], "verbosity": 2, "params": dcc_params, "pos_arg": "pos"}


def task_init():
    """ Initialize docker & django project. """

    return {
        "actions": [
            Interactive("cookiecutter git@bitbucket.org:appchance/pychance-cookiecutter.git"),
            CmdAction(
                (
                    "cd $(ls -td -- */ | head -n 1) && "
                    "ln -s docker/local/compose.yml ./docker-compose.yml &&"
                    "cp -r .envs/.local.example .envs/.local"
                )
            ),
            CmdAction(
                "cd $(ls -td -- */ | head -n 1) && dodo build && dodo upd && dodo manage makemigrations && dodo manage migrate && dodo logs"
            ),
        ],
        "verbosity": 2,
    }


def task_build():
    """ Build local docker images. """

    def dcc(compose_cmd, dj_service):
        return f"{compose_cmd} build"

    return {"actions": [Interactive(dcc)], "verbosity": 2, "params": dcc_params, "pos_arg": "pos"}


def task_upd():
    """ Start local docker containers in detatched mode. """

    def dcc(compose_cmd, dj_service):
        return f"{compose_cmd} up -d"

    return {"actions": [Interactive(dcc)], "verbosity": 2, "params": dcc_params, "pos_arg": "pos"}


def task_logs():
    """ Follow docker logs. """

    def dcc(compose_cmd, dj_service):
        return f"{compose_cmd} logs -f"

    return {"actions": [Interactive(dcc)], "verbosity": 2, "params": dcc_params, "pos_arg": "pos"}


def task_stop():
    """ Stop docker containers. """

    def dcc(compose_cmd, dj_service):
        return f"{compose_cmd} stop"

    return {"actions": [Interactive(dcc)], "verbosity": 2, "params": dcc_params, "pos_arg": "pos"}


def task_down():
    """ Send docker-compose down command. """

    def dcc(compose_cmd, dj_service):
        return f"{compose_cmd} down"

    return {"actions": [Interactive(dcc)], "verbosity": 2, "params": dcc_params, "pos_arg": "pos"}


def task_attach():
    """ Attach to django service. """

    def dcc(compose_cmd, dj_service):
        return f"{compose_cmd} attach {dj_service}"

    return {"actions": [Interactive(dcc)], "verbosity": 2, "params": dcc_params, "pos_arg": "pos"}


def task_pip():
    """ Run pip command. """

    def dcc(pos, compose_cmd, dj_service):
        arguments_space = " ".join(pos)
        return f"{compose_cmd} exec {dj_service} pip {pos}"

    return {"actions": [Interactive(dcc)], "verbosity": 2, "params": dcc_params, "pos_arg": "pos"}


def task_manage():
    """ Run django manage.py command with additional arguments. """

    def dcc(pos, compose_cmd, dj_service):
        return f"{compose_cmd} run --rm {dj_service} python manage.py {' '.join(pos)}"

    return {"actions": [Interactive(dcc)], "verbosity": 2, "params": dcc_params, "pos_arg": "pos"}


def task_test():
    """ Run pytest. """

    def dcc(pos, compose_cmd, dj_service):
        return f"{compose_cmd} exec {dj_service} pytest {' '.join(pos)}"

    return {"actions": [Interactive(dcc)], "verbosity": 2, "params": dcc_params, "pos_arg": "pos"}


def task_format():
    """ Format code. """

    def dcc(pos, compose_cmd, dj_service):
        return [
            f'{compose_cmd} run --rm {dj_service}   /bin/bash -c  "isort . && black -l 120 ."',
        ]

    return {"actions": [Interactive(dcc)], "verbosity": 2, "params": dcc_params, "pos_arg": "pos"}


def task_shell():
    """ Open django shell. """

    def dcc(pos, compose_cmd, dj_service):
        return f"{compose_cmd} run --rm  {dj_service} python manage.py shell_plus"

    return {"actions": [Interactive(dcc)], "verbosity": 2, "params": dcc_params, "pos_arg": "pos"}


def task_migrations():
    """ Django make & run migrations. """

    def dcc(compose_cmd, dj_service):
        return [
            f"{compose_cmd} run --rm  {dj_service} python manage.py makemigrations",
            f"{compose_cmd} run --rm  {dj_service} python manage.py migrate",
        ]

    return {"actions": [Interactive(dcc)], "verbosity": 2, "params": dcc_params}
