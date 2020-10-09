import pytest
import docker
import time
import requests
import logging
import os
from pathlib import Path
from shutil import copyfile

logger = logging.getLogger()

client = docker.from_env()
container_name = "test-aoa-img"
max_retries = 10


def pytest_addoption(parser):
    parser.addoption("--img", action="store", help="specify image name")
    parser.addoption("--port", action="store", help="specify port number")
    parser.addoption("--skip-docker", action="store_true", help="don't start the docker container")


def check_aoa_up(aoa_url, auth):
    retries = 0
    while retries < max_retries:
        try:
            resp = requests.get(
                url=aoa_url + "/admin/health",
                auth=auth
            )
            return resp.status_code
        except:
            logger.info('AOA test container... waiting')
            retries += 1
            time.sleep(5)
    assert (5 == 4), 'AOA test container... unable to access'


@pytest.fixture(scope="session")
def setup(request, tmpdir_factory):
    skip_docker = request.config.getoption("--skip-docker", False)

    if not skip_docker:
        img_name = request.config.getoption("--img") if request.config.getoption("--img") is not None \
    else "thinkbiganalytics/aoa-core:master"
        port_number = request.config.getoption("--port") if request.config.getoption("--port") is not None \
            else 8080

        logger.info("AOA test container using image {} and port {}".format(img_name, port_number))
        logger.info("AOA test container... starting")
        client.containers.run(image=img_name,
                              name=container_name,
                              auto_remove=True,
                              privileged=True,
                              ports={
                                  '8080/tcp': port_number,
                                  '9000/tcp': 9000,
                                  '61613/tcp': 61613
                              },
                              volumes={
                                  '/var/run/docker.sock': {
                                      'bind': '/var/run/docker.sock'
                                  }
                              },
                              detach=True)

        def fin():
            logger.info('AOA test container... removing')
            client.containers.list(all=True, filters={
                "name": container_name
            })[0].remove(force=True)
            logger.info('AOA test container... removed')

        request.addfinalizer(fin)

    from aoa.api_client import AoaClient
    pytest.aoa_client = AoaClient(aoa_url="http://localhost:8080",
                                  auth_mode="basic",
                                  auth_user="admin",
                                  auth_pass="admin")
    pytest.aoa_client.set_project_id("23e1df4b-b630-47a1-ab80-7ad5385fcd8d")
    pytest.module_dir = os.path.join(os.path.dirname(__file__).replace('/tests', ''))
    pytest.aoa_script = os.path.join(pytest.module_dir, 'aoacli.py')
    copyfile(os.path.join(pytest.module_dir, 'scripts/aoa'), pytest.aoa_script)
    os.chmod(pytest.aoa_script, 0o755)

    check_aoa_up(pytest.aoa_client.aoa_url, pytest.aoa_client.auth)
    logger.info('AOA test container... started')

    temp_dir = tmpdir_factory.mktemp("aoa_cli_dir")
    model_temp_dir = os.path.join(str(temp_dir), "model_definitions")
    pytest.temp_dir = temp_dir
    pytest.model_temp_dir = model_temp_dir
    pytest.getbasetemp = tmpdir_factory.getbasetemp
    pytest.command_name = 'aoa'
    logger.debug("AOA testing directory structure created at {}".format(temp_dir))
    logger.info("AOA testing model directory structure created at {}".format(model_temp_dir))

    def cleanup():
        file_to_remove = Path(pytest.aoa_script)
        file_to_remove.unlink()

    request.addfinalizer(cleanup)
