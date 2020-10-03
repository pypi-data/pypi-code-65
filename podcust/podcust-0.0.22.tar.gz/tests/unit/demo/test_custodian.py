"""
Unit Tests for DemoCust class.
"""
from podcust.demo import custodian
import mock
from subprocess import CompletedProcess
import pytest


class TestDemoCust:
    def setup_class(cls):
        cls.demo = custodian.DemoCust()

    @mock.patch("podcust.demo.custodian.subprocess.run")
    def test_find_stored_image(self, mocked_run):
        """
        Example output from podman images:
        REPOSITORY                         TAG     IMAGE ID      CREATED       SIZE
        localhost/httpdemo                 latest  5ff443b54997  46 hours ago  582 MB

        The hardcoded result needs to be updated properly, from a an eralier run test!
        """
        mocked_run.return_value = CompletedProcess(
            args="podman images",
            returncode=0,
            stdout=(
                "REPOSITORY                         TAG     IMAGE ID      CREATED       SIZE\n"
                "localhost/httpdemo                 latest  5ff443b54997  46 hours ago  582 MB\n"
                "registry.fedoraproject.org/fedora  latest  00ff39a8bf19  2 months ago  189 MB"
            ),
            stderr="",
        )
        result = self.demo.find_stored_image_id()
        assert result == ["5ff443b54997"]

    @mock.patch("podcust.demo.custodian.DemoCust.find_stored_image_id")
    @mock.patch("podcust.demo.custodian.subprocess.run")
    def test_remove_stored_image(self, mocked_run, mocked_image):
        """"""
        mocked_image.return_value = ["5ff443b54997"]
        self.demo.remove_stored_image()
        mocked_run.assert_called_with(
            "podman image rm 5ff443b54997",
            text=True,
            shell=True,
            stdout=-1,
            stderr=-1,
            check=True,
        )

    @mock.patch("podcust.demo.custodian.subprocess.run")
    def test_find_exited_containers(self, mocked_run):
        """
        Example output for container images:
        $ podman ps -a  # noqa: E501
        CONTAINER ID  IMAGE                                     COMMAND     CREATED     STATUS                   PORTS                 NAMES
        1b5fe6643ece  localhost/httpdemo:latest                 /sbin/init  2 days ago  Exited (0) 2 days ago    0.0.0.0:8080->80/tcp  strange_wu
        3ea6bf480c47  localhost/httpdemo:latest                 /bin/bash   2 days ago  Exited (0) 2 days ago    0.0.0.0:8080->80/tcp  funny_williams
        63604b048bc9  registry.fedoraproject.org/fedora:latest  /bin/bash   2 days ago  Exited (0) 2 days ago                          practical_kowalevski
        b3e4d5b363ce  localhost/httpdemo:latest                 /sbin/init  2 days ago  Exited (137) 2 days ago  0.0.0.0:8080->80/tcp  pedantic_tesla
        c4e4a6847c3d  localhost/httpdemo:latest                 /bin/bash   2 days ago  Exited (0) 2 days ago    0.0.0.0:8080->80/tcp  jolly_volhard
        dc9bffeef1c2  registry.fedoraproject.org/fedora:latest  /bin/bash   2 days ago  Exited (0) 2 days ago    0.0.0.0:8080->80/tcp  zealous_blackburn0


        The hardcoded result needs to be updated properly, from a an eralier run test!
        """
        mocked_run.return_value = CompletedProcess(
            args="podman images",
            returncode=0,
            stdout=(  # noqa: E501
                "CONTAINER ID  IMAGE                                     COMMAND     CREATED     STATUS                   PORTS                 NAMES\n"  # noqa: E501
                "1b5fe6643ece  localhost/httpdemo:latest                 /sbin/init  2 days ago  Exited (0) 2 days ago    0.0.0.0:8080->80/tcp  strange_wu\n"  # noqa: E501
                "63604b048bc9  registry.fedoraproject.org/fedora:latest  /bin/bash   2 days ago  Exited (0) 2 days ago                          practical_kowalevski"  # noqa: E501
            ),
            stderr="",
        )
        result = self.demo.find_exited_containers()
        assert result == ["1b5fe6643ece"]

    @mock.patch("podcust.demo.custodian.DemoCust.find_exited_containers")
    @mock.patch("podcust.demo.custodian.subprocess.run")
    def test_remove_exited_containers(self, mocked_run, mocked_ec):
        """"""
        mocked_ec.return_value = ["5ff443b54997"]
        self.demo.removed_exited_containers()
        mocked_run.assert_called_with(
            "podman container rm 5ff443b54997",
            text=True,
            shell=True,
            stdout=-1,
            stderr=-1,
            check=True,
        )

    @mock.patch("podcust.demo.custodian.__file__", "/home/user/file.py")
    @mock.patch("podcust.demo.custodian.subprocess.run")
    def test_demo_build_demo_image(self, mocked_run):
        """"""
        self.demo.build_demo_image()
        mocked_run.assert_called_with(
            "podman build -f /home/user/Dockerfile -t httpdemo",
            text=True,
            shell=True,
            stdout=-1,
            stderr=-1,
            check=True,
        )

    @mock.patch("podcust.demo.custodian.subprocess.run")
    def test_get_running_container_id(self, mocked_run):
        """"""

        mocked_run.return_value = CompletedProcess(
            args="podman ps",
            returncode=0,
            stdout=(
                "CONTAINER ID  IMAGE                      COMMAND     CREATED         STATUS             PORTS                 NAMES\n"  # noqa: E501
                "71440253d707  localhost/httpdemo:latest  /sbin/init  21 minutes ago  Up 21 minutes ago  0.0.0.0:8080->80/tcp  pedantic_chatelet\n"  # noqa: E501
            ),
            stderr="",
        )

        self.demo.get_running_container_id()
        assert self.demo.running_container_id == "71440253d707"

    @mock.patch("podcust.demo.custodian.subprocess.run")
    def test_get_running_container_id_exception(self, mocked_run):
        """

        Note:
        The test works because the class has been populated with the running id from
        the previous test test_get_running_container_id.
        """

        mocked_run.return_value = CompletedProcess(
            args="podman ps",
            returncode=0,
            stdout=(
                "CONTAINER ID  IMAGE                      COMMAND     CREATED         STATUS             PORTS                 NAMES\n"  # noqa: E501
                "71440253d708  localhost/httpdemo:latest  /sbin/init  21 minutes ago  Up 21 minutes ago  0.0.0.0:8080->80/tcp  pedantic_chatelet\n"  # noqa: E501
                "71440253d709  localhost/httpdemo:latest  /sbin/init  21 minutes ago  Up 21 minutes ago  0.0.0.0:8080->80/tcp  pedantic_chatelet\n"  # noqa: E501
            ),
            stderr="",
        )

        with pytest.raises(custodian.MultipleContainers) as exc:
            self.demo.get_running_container_id()

        assert str(exc.value) == (
            "Duplicate container instance 71440253d708 found while 71440253d707 is also running."
        )

    @mock.patch("podcust.demo.custodian.subprocess.run")
    def test_run_container(self, mocked_run):
        """
        Note: Because this test assigns running_container_id it has to run after
        test_demo_get_running_container_id and test_demo_get_running_container_id_exception.
        """

        mocked_run.return_value = CompletedProcess(
            args="podman run -d -p 8080:80 localhost/httpdemo",
            returncode=0,
            stdout=("71440253d707c083ddfaf1e47b3bf9db37d3d0189d232237daac128f4a4aa9f0"),
            stderr="",
        )

        self.demo.run_container()
        assert (
            self.demo.running_container_id
            == "71440253d707c083ddfaf1e47b3bf9db37d3d0189d232237daac128f4a4aa9f0"
        )

    @mock.patch("podcust.demo.custodian.subprocess.run")
    def test_stop_container(self, mocked_run):
        """"""
        self.demo.stop_container()
        mocked_run.assert_called_with(
            "podman kill 71440253d707c083ddfaf1e47b3bf9db37d3d0189d232237daac128f4a4aa9f0",
            text=True,
            shell=True,
            stdout=-1,
            stderr=-1,
            check=True,
        )

    @mock.patch("podcust.demo.custodian.subprocess.run")
    def test_activate_container(self, mocked_run):
        """"""
        self.demo.running_container_id == "71440253d708"
        mocked_run.return_value = CompletedProcess(
            args="podman ps",
            returncode=0,
            stdout=(
                "CONTAINER ID  IMAGE                      COMMAND     CREATED         STATUS             PORTS                 NAMES\n"  # noqa: E501
                "71440253d708  localhost/httpdemo:latest  /sbin/init  21 minutes ago  Up 21 minutes ago  0.0.0.0:8080->80/tcp  pedantic_chatelet\n"  # noqa: E501
            ),
            stderr="",
        )
        self.demo.activate_container()
        mocked_run.assert_called_with(
            "podman exec 71440253d708 systemctl start httpd",
            text=True,
            shell=True,
            stdout=-1,
            stderr=-1,
            check=True,
        )

    @mock.patch("podcust.demo.custodian.subprocess.run")
    def test_deactivate_container(self, mocked_run):
        """"""
        self.demo.running_container_id == "71440253d708"
        mocked_run.return_value = CompletedProcess(
            args="podman ps",
            returncode=0,
            stdout=(
                "CONTAINER ID  IMAGE                      COMMAND     CREATED         STATUS             PORTS                 NAMES\n"  # noqa: E501
                "71440253d708  localhost/httpdemo:latest  /sbin/init  21 minutes ago  Up 21 minutes ago  0.0.0.0:8080->80/tcp  pedantic_chatelet\n"  # noqa: E501
            ),
            stderr="",
        )
        self.demo.deactivate_container()
        mocked_run.assert_called_with(
            "podman exec 71440253d708 systemctl stop httpd",
            text=True,
            shell=True,
            stdout=-1,
            stderr=-1,
            check=True,
        )


class TestDemoCust2:
    def setup_class(cls):
        cls.demo = custodian.DemoCust()

    @mock.patch("podcust.demo.custodian.subprocess.run")
    def test_get_running_container_id_missing(self, mocked_run):
        """"""

        mocked_run.return_value = CompletedProcess(
            args="podman ps",
            returncode=0,
            stdout=(
                "CONTAINER ID  IMAGE                      COMMAND     CREATED         STATUS             PORTS                 NAMES\n"  # noqa: E501
                "71440253d707  localhost/other:latest  /sbin/init  21 minutes ago  Up 21 minutes ago  0.0.0.0:8080->80/tcp  pedantic_chatelet\n"  # noqa: E501
                "71440253d708  localhost/other:latest  /sbin/init  21 minutes ago  Up 21 minutes ago  0.0.0.0:8080->80/tcp  pedantic_chatelet\n"  # noqa: E501
            ),
            stderr="",
        )

        with pytest.raises(custodian.MissingContainers) as exc:
            self.demo.get_running_container_id()

        assert str(exc.value) == "No instance of localhost/httpdemo is running!"
