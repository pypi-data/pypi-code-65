import random
from contextlib import contextmanager

import pytest
from click.testing import CliRunner
from expects import *

from sym.cli.sym import sym as click_command
from sym.cli.tests.matchers import succeed

INSTANCES = [
    "i-06d0713fa5088af8a",
    "i-0be1604b653df5559",
    "i-0315649e38959c83a",
    "i-057f8375f72fa86d7",
    "i-037eb6769decdad1e",
    "i-02e94f9f185603233",
    "i-0d7c7f0671a73b938",
    "i-09baf4db5ab86c59b",
    "i-0961d3254d4c6a453",
    "i-0f7adaa5432f7a6d4",
    "i-0c3d1eee13d118a2c",
]


@pytest.fixture
def integration_runner(capfdbinary, sandbox):
    @contextmanager
    def context():
        runner = CliRunner()
        with sandbox.push_xdg_config_home():

            def run(*args):
                result = runner.invoke(click_command, args, catch_exceptions=False)
                cap = capfdbinary.readouterr()
                result.stdout_bytes = cap.out
                result.stderr_bytes = cap.err

                expect(result).to(succeed())
                return result

            yield run

    return context


def pytest_addoption(parser):
    parser.addoption("--email", default="ci@symops.io")
    parser.addoption("--org", default="sym")
    parser.addoption("--instance", default=random.choice(INSTANCES))
    parser.addoption("--resource", default="test")
