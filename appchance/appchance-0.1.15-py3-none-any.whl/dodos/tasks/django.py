from doit.tools import Interactive
from doit.action import CmdAction

DJANGO_COMPOSE_CMD = "docker-compose"
DJANGO_SERVICE_NAME = "django"

def task_build():
    """ Build local docker images """
    return {
      "actions": [
          f"{DJANGO_COMPOSE_CMD} build"
      ],
      "verbosity": 2
    }


def task_up():
    """ Start local docker containers  """
    return {
      "actions": [
          Interactive(f"{DJANGO_COMPOSE_CMD} up")
      ],
      "verbosity": 2
    }


def task_upd():
    """ Start local docker containers in detatched mode """
    return {
      "actions": [
          f"{DJANGO_COMPOSE_CMD} up -d"
      ],
      "verbosity": 2
    }


def task_logs():
    """ Follow docker logs """
    return {
      "actions": [
          f"{DJANGO_COMPOSE_CMD} logs -f"
      ],
      "verbosity": 2
    }


def task_stop():
    """ Stop docker containers """
    return {
      "actions": [
          f"{DJANGO_COMPOSE_CMD} stop"
      ],
      "verbosity": 2
    }


def task_down():
    """ Kill docker containers """
    return {
      "actions": [
          f"{DJANGO_COMPOSE_CMD} down"
      ],
      "verbosity": 2
    }


def task_attach():
    """ Create django superuser """
    return {
        "actions": [
            Interactive(f"{DJANGO_COMPOSE_CMD} attach {DJANGO_SERVICE_NAME}")
        ],
        "verbosity": 2
    }


def task_pip():
    """ Run pip command. """

    def pass_arguments(pos):
        arguments_space = " ".join(pos)
        return f"{DJANGO_COMPOSE_CMD} exec {DJANGO_SERVICE_NAME} pip {arguments_space}"

    return {
        "actions": [Interactive(pass_arguments)],
        "verbosity": 2,
        'pos_arg': 'pos'
    }


def task_manage():
    """ run django manage.py command """

    def argv(pos):
        return f"{DJANGO_COMPOSE_CMD} run --rm {DJANGO_SERVICE_NAME} python manage.py {' '.join(pos)}"

    return {
        "actions": [Interactive(argv)],
        "verbosity": 2,
        "pos_arg": "pos"
    }


def task_shell():
    """ Open django shell """

    return {
        "actions": [Interactive(f"{DJANGO_COMPOSE_CMD} run --rm {DJANGO_SERVICE_NAME} python manage.py shell_plus")],
        "verbosity": 2
    }


def task_migrations():
    """ Django make & run migrations """
    return {
        "actions": [
            Interactive(f"{DJANGO_COMPOSE_CMD} run --rm {DJANGO_SERVICE_NAME} python manage.py makemigrations"),
            Interactive(f"{DJANGO_COMPOSE_CMD} run --rm {DJANGO_SERVICE_NAME} python manage.py migrate")
        ],
        "verbosity": 2
    }


def task_format():
    """ Format code """

    return {
        "actions": [
            f"{DJANGO_COMPOSE_CMD} exec {DJANGO_SERVICE_NAME} isort --recursive apps",
            f"{DJANGO_COMPOSE_CMD} exec {DJANGO_SERVICE_NAME} black -l 120 .",
        ],
        "verbosity": 2,
    }


def task_test():
    """ Run pytest """

    def pass_arguments(pos):
        arguments_space = " ".join(pos)
        return f"{DJANGO_COMPOSE_CMD} exec {DJANGO_SERVICE_NAME} pytest {arguments_space}"

    return {"actions": [Interactive(pass_arguments)], "verbosity": 2, "pos_arg": "pos"}
