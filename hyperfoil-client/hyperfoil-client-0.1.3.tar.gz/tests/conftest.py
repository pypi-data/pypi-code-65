import os

import pytest
import yaml
from dotenv import load_dotenv

from hyperfoil import HyperfoilClient


load_dotenv()


@pytest.fixture(scope='session')
def url() -> str:
    return os.getenv('HYPERFOIL_URL')


@pytest.fixture(scope='session')
def client(url) -> HyperfoilClient:
    return HyperfoilClient(url)


@pytest.fixture(scope='session')
def benchmark(client):
    return client.benchmark


@pytest.fixture(scope='session')
def run(client):
    return client.run


@pytest.fixture(scope='session')
def benchmark_yaml():
    with open('benchmarks/hello-world.yaml') as file:
        data = file.read()
    return yaml.load(data, Loader=yaml.Loader)


@pytest.fixture(scope='session')
def benchmark_file():
    with open('benchmarks/file-benchmark.hf.yaml') as file:
        data = file.read()
    return yaml.load(data, Loader=yaml.Loader)
