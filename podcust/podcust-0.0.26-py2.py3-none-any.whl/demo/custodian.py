"""
Custodian Class for Demo container.
"""

from typing import List
import subprocess
from pathlib import Path, PurePath
import requests
from bs4 import BeautifulSoup  # type: ignore


class MultipleContainers(Exception):
    """
    Exception raised when more than one containers of a type are running.

    Inspired from:
    https://www.programiz.com/python-programming/user-defined-exception

    :param container_id1: First container id of container type
    :param container_id2: Second container id of container type.
        message -- explanation of the error
    """

    def __init__(self, container_id1, container_id2):
        self.container_id1 = container_id1
        self.container_id2 = container_id2
        self.message = (
            f"Duplicate container instance {container_id2} found while {container_id1}"
            " is also running."
        )
        super().__init__(self.message)


class MissingContainers(Exception):
    """
    Exception raised when not one containers of expected type are running.

    Inspired from:
    https://www.programiz.com/python-programming/user-defined-exception

    :param container_name: Name of container image.
        message -- explanation of the error
    """

    def __init__(self, container_name):
        self.message = f"No instance of {container_name} is running!"
        super().__init__(self.message)


class ContainerHealthError(Exception):
    """
    Exception raised when a container fails it's health check.

    Inspired from:
    https://www.programiz.com/python-programming/user-defined-exception

    :param container_name: Name of container image.
    :param container_id: Running Container id of container type container_name
        message -- explanation of the error
    """

    def __init__(self, container_name, container_id):
        self.message = (
            f"Failed health check for {container_name} with id: {container_id}"
        )
        super().__init__(self.message)


class DemoCust:
    """
    Main class for handling the httpdemo container.

    The httpdemo container just spawns an a container with an apache web server
    service serving the Fedora Test page through http.

    :param name: The Repository name of the image this class is custodian for.
    """

    name: str
    image_id: str

    def __init__(self, name: str = "localhost/httpdemo"):
        """
        Initialize DemoCust class.
        """
        self.name = name
        self.image_id = ""
        self.running_container_id = ""

    def find_stored_image_id(self) -> List[str]:
        """
        This function looks if the system has an appropriate container image and
        returns the id of that image.

        Current implementation assumes that the first match is the one we are after.

        TODO: Specify what tag we want to match?
        """

        image_id_list: List[str] = []
        check = subprocess.run(
            "podman images",
            text=True,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # split results line by line and remove all but one whitespace
        processed_lines = []
        for line in check.stdout.splitlines():
            # default split separator is spaces, too many spaces act as one separator
            tmp = " ".join(line.split())
            processed_lines.append(tmp.split(" "))

        # We expect the first line to have the columns below:
        # ['REPOSITORY', 'TAG', 'IMAGE', 'ID', 'CREATED', 'SIZE']
        for il in processed_lines:
            if il[0] == self.name:
                image_id_list.append(il[2])

        return image_id_list

    def remove_stored_image(self):
        """
        Removes a stored container image corresponding to the name
        the class has been instantiated to.
        """

        image_id_list = self.find_stored_image_id()
        command_text = "podman image rm $image_id"

        for iid in image_id_list:
            command_text = command_text.replace("$image_id", iid)
            print(f"Removing image {self.name} with image id {iid}")
            try:
                subprocess.run(
                    command_text,
                    text=True,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )
            except Exception as e:
                print(e)

    def find_exited_containers(self):  # noqa: E501
        """
        Find all containers of demo type that have run and exited.

        You can see here a sample output of the command we use to find the containers we want
        to remove:  # noqa: E501
        $ podman ps -a
        CONTAINER ID  IMAGE                                     COMMAND     CREATED     STATUS                   PORTS                 NAMES
        1b5fe6643ece  localhost/httpdemo:latest                 /sbin/init  2 days ago  Exited (0) 2 days ago    0.0.0.0:8080->80/tcp  strange_wu
        3ea6bf480c47  localhost/httpdemo:latest                 /bin/bash   2 days ago  Exited (0) 2 days ago    0.0.0.0:8080->80/tcp  funny_williams
        63604b048bc9  registry.fedoraproject.org/fedora:latest  /bin/bash   2 days ago  Exited (0) 2 days ago                          practical_kowalevski
        b3e4d5b363ce  localhost/httpdemo:latest                 /sbin/init  2 days ago  Exited (137) 2 days ago  0.0.0.0:8080->80/tcp  pedantic_tesla
        c4e4a6847c3d  localhost/httpdemo:latest                 /bin/bash   2 days ago  Exited (0) 2 days ago    0.0.0.0:8080->80/tcp  jolly_volhard
        dc9bffeef1c2  registry.fedoraproject.org/fedora:latest  /bin/bash   2 days ago  Exited (0) 2 days ago    0.0.0.0:8080->80/tcp  zealous_blackburn0
        """

        container_id_list: List[str] = []
        check = subprocess.run(
            "podman ps -a",
            text=True,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        # split results line by line and remove all but one whitespace
        processed_lines = []
        for line in check.stdout.splitlines():
            # default split separator is spaces, too many spaces act as one separator
            tmp = " ".join(line.split())
            processed_lines.append(tmp.split(" "))

        # We expect the first line to have the columns below:
        # ['CONTAINER ID', 'IMAGE', 'COMMAND', 'CREATED', 'CREATED', 'STATUS', 'PORTS', 'NAMES']
        for il in processed_lines:
            container_name = il[1].split(":")[0]
            status = il[6]

            if container_name == self.name and status == "Exited":
                container_id_list.append(il[0])

        return container_id_list

    def removed_exited_containers(self):
        """
        Remove all containers of demo type that have run and exited.

        Remove an image with:
        podman container rm 3ea6bf480c47
        """

        container_id_list = self.find_exited_containers()

        for cont in container_id_list:

            try:
                print(f"Removing container {self.name} with container id {cont}")
                command_text = "podman container rm $container_id"
                command_text = command_text.replace("$container_id", cont)
                subprocess.run(
                    command_text,
                    text=True,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )

            except Exception as e:
                print(e)

    def build_demo_image(self):
        """
        Build an image for the demo container. Use the dockerfile located at this folder.

        The command to build a container is:
        podman build -f Dockerfile -t httpdemo
        """

        command_text = "podman build -f $dockerfile -t httpdemo"
        dockerfile_dir = str(PurePath.joinpath(Path(__file__).parent, "Dockerfile"))
        command_text = command_text.replace("$dockerfile", dockerfile_dir)

        try:
            p = subprocess.run(
                command_text,
                text=True,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            print(p.stdout)

        except Exception as e:
            print(e)

    def run_container(self):
        """
        Start running the demo container.
        """
        command_text = "podman run -d -p 8080:80 localhost/httpdemo"
        try:
            p = subprocess.run(
                command_text,
                text=True,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            print(p.stdout)
            self.running_container_id = p.stdout

        except Exception as e:
            print(e)

    def get_running_container_id(self):
        """
        Get the container ID for a running container (of demo type).
        """
        command_text = "podman ps"
        p = subprocess.run(
            command_text,
            text=True,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        # split results line by line and remove all but one whitespace
        processed_lines = []
        for line in p.stdout.splitlines():
            # default split separator is spaces, too many spaces 'act' as one separator
            tmp = " ".join(line.split())
            processed_lines.append(tmp.split(" "))

        # We expect the first line to have the columns below:
        # ['CONTAINER ID', 'IMAGE', 'COMMAND', 'CREATED', 'CREATED', 'STATUS', 'PORTS', 'NAMES']
        for il in processed_lines:
            container_name = il[1].split(":")[0]
            status = il[6]

            if container_name == self.name and status == "Up":
                if self.running_container_id == "":
                    self.running_container_id = il[0]
                else:
                    raise MultipleContainers(self.running_container_id, il[0])
        # raise error if no container is found
        if self.running_container_id == "":
            raise MissingContainers(self.name)

    def stop_container(self):
        """
        Stop demo running container.
        """
        command_text: str = "podman kill $container_id"
        # if container_id not register, retrieve it
        if self.running_container_id == "":
            self.get_running_container_id()

        command_text = command_text.replace("$container_id", self.running_container_id)

        try:
            subprocess.run(
                command_text,
                text=True,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.running_container_id = ""

        except Exception as e:
            print(e)

    def activate_container(self):
        """
        Activate a demo's container httpd service.
        """
        command_text: str = "podman exec $container_id systemctl start httpd"
        # if container_id not register, retrieve it
        if self.running_container_id == "":
            self.get_running_container_id()

        command_text = command_text.replace("$container_id", self.running_container_id)

        try:
            subprocess.run(
                command_text,
                text=True,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.running_container_id = ""

        except Exception as e:
            print(e)

    def deactivate_container(self):
        """
        Deactivate a demo's container httpd service.
        """
        command_text: str = "podman exec $container_id systemctl stop httpd"
        # if container_id not register, retrieve it
        if self.running_container_id == "":
            self.get_running_container_id()

        command_text = command_text.replace("$container_id", self.running_container_id)

        try:
            subprocess.run(
                command_text,
                text=True,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.running_container_id = ""

        except Exception as e:
            print(e)

    def health_check(self):
        """
        Runs basic checks to test container's functionality.

        Verifying health check inspired by:
        https://stackoverflow.com/a/51242/1904901
        """

        req = requests.get("http://127.0.0.1:8080/")

        # parse the content
        soup = BeautifulSoup(req.text, features="html5lib")
        title = soup.find("title")

        if title.text == "Test Page for the HTTP Server on Fedora":
            print("Health check succeeded!")
        else:
            raise ContainerHealthError(self.name, self.running_container_id)
