from doit.tools import Interactive
from doit.action import CmdAction

from doit.tools import Interactive
from doit.action import CmdAction

dcc_params = [
    {
        'name':'compose_cmd',
        'short':'compose_cmd',
        'long': 'compose_cmd',
        'type': str,
        'default': 'docker-compose'
    },
    {
        'name':'dj_service',
        'short':'dj_service',
        'long': 'dj_service',
        'type': str,
        'default': 'django'
    }
]


def task_build():
    """ Build local docker images """

    def dcc(compose_cmd, dj_service):
        return f"{compose_cmd} build"

    return {
        "actions": [Interactive(dcc)],
        "params": dcc_params,
        'verbosity': 2
    }


def task_up():
    """ Start local docker containers  """

    def dcc(compose_cmd, dj_service):
        return f"{compose_cmd} up"

    return {
        "actions": [Interactive(dcc)],
        "params": dcc_params,
        'verbosity': 2
    }


def task_upd():
    """ Start local docker containers in detatched mode """

    def dcc(compose_cmd, dj_service):
        return f"{compose_cmd} up -d"

    return {
        "actions": [Interactive(dcc)],
        "params": dcc_params,
        'verbosity': 2
    }


def task_logs():
    """ Follow docker logs """

    def dcc(compose_cmd, dj_service):
        return f"{compose_cmd} logs -f"

    return {
        "actions": [Interactive(dcc)],
        "params": dcc_params,
        'verbosity': 2
    }


def task_stop():
    """ Stop docker containers """

    def dcc(compose_cmd, dj_service):
        return f"{compose_cmd} stop"

    return {
        "actions": [Interactive(dcc)],
        "params": dcc_params,
        'verbosity': 2
    }


def task_down():
    """ Kill docker containers """

    def dcc(compose_cmd, dj_service):
        return f"{compose_cmd} down"

    return {
        "actions": [Interactive(dcc)],
        "params": dcc_params,
        'verbosity': 2
    }


def task_attach():
    """ Create django superuser """

    def dcc(compose_cmd, dj_service):
        return f"{compose_cmd} attach {dj_service}"

    return {
        "actions": [Interactive(dcc)],
        "params": dcc_params,
        'verbosity': 2
    }


def task_pip():
    """ Run pip command. """

    def dcc(pos, compose_cmd, dj_service):
        arguments_space = " ".join(pos)
        return f"{compose_cmd} exec {dj_service} pip {pos}"

    return {
        "actions": [Interactive(dcc)],
        "params": dcc_params,
        'verbosity': 2,
        'pos_arg': 'pos'
    }


# TODO: translate to new format
# def task_manage():
#     """ run django manage.py command """

#     def argv(pos):
#         return f"{DJANGO_COMPOSE_CMD} run --rm {DJANGO_SERVICE_NAME} python manage.py {' '.join(pos)}"

#     return {
#         "actions": [Interactive(argv)],
#         "verbosity": 2,
#         "pos_arg": "pos"
#     }


# def task_shell():
#     """ Open django shell """

#     return {
#         "actions": [Interactive(f"{DJANGO_COMPOSE_CMD} run --rm {DJANGO_SERVICE_NAME} python manage.py shell_plus")],
#         "verbosity": 2
#     }


# def task_migrations():
#     """ Django make & run migrations """
#     return {
#         "actions": [
#             Interactive(f"{DJANGO_COMPOSE_CMD} run --rm {DJANGO_SERVICE_NAME} python manage.py makemigrations"),
#             Interactive(f"{DJANGO_COMPOSE_CMD} run --rm {DJANGO_SERVICE_NAME} python manage.py migrate")
#         ],
#         "verbosity": 2
#     }


# def task_format():
#     """ Format code """

#     return {
#         "actions": [
#             f"{DJANGO_COMPOSE_CMD} exec {DJANGO_SERVICE_NAME} isort --recursive apps",
#             f"{DJANGO_COMPOSE_CMD} exec {DJANGO_SERVICE_NAME} black -l 120 .",
#         ],
#         "verbosity": 2,
#     }


# def task_test():
#     """ Run pytest """

#     def pass_arguments(pos):
#         arguments_space = " ".join(pos)
#         return f"{DJANGO_COMPOSE_CMD} exec {DJANGO_SERVICE_NAME} pytest {arguments_space}"

#     return {"actions": [Interactive(pass_arguments)], "verbosity": 2, "pos_arg": "pos"}
