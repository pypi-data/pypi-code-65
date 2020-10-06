import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

INSTALL_DIR = os.getenv("INSTALL_DIR", "/opt/rexsio")
ROOT_DIR = f"{INSTALL_DIR}/agent"
BASE_SERVICES_PATH = f"{INSTALL_DIR}/services"
ACCESS_TOKEN_PATH = f"{ROOT_DIR}/access.token"
REXSIO_HOST = os.getenv("REXSIO_HOST", "api-dev.rexs.io")
REXSIO_WS_HOST = os.getenv("REXSIO_WS_HOST", "ws-service.rexsio.dev.dac.systems")
REXSIO_USER = os.getenv("REXSIO_USER", "rexsio")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "rexsio")
RABBITMQ_BASE_URL = os.getenv("RABBITMQ_BASE_URL", "localhost")
RABBITMQ_URL = f"amqp://rexsio:{RABBITMQ_PASS}@{RABBITMQ_BASE_URL}:5672"
