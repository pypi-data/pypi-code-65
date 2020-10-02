# Project configuration

# Specify command with path to your docker compose file.
DOCKER_COMPOSE_CMD = "docker-compose -f docker-compose.yml"

# Service name running django in docker-compose file.
DJANGO_SERVICE_NAME = "django"
DJANGO_APPS_DIR = "apps"

# Active task modules.
TASK_MODULES = [
    # "python",
    "docker_django",
]

# Place to specify your custom tasks.
CUSTOM_TASKS = []
