"""
Retrieve Information about the platform the package is running on.
"""

import subprocess


def podman_exists():
    """
    Check that the podman package is installed and working properly.
    Raise an OSError if the podman --version command does not complete successfully.
    """

    check = subprocess.run(
        "podman --version",
        text=True,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if check.returncode != 0:
        raise OSError("podman package is not available!")
