"""
Main module.
"""

from pathlib import PosixPath, Path
from shutil import chown
from pwd import getpwuid
from os import getuid
import logging


class CommonFolder:
    """

    Main class regarding management of a folder that is commonly used across many users.

    - The class creates a logfile at /tmp/fcust/$USER.log
    - By default the class assumes that the root of the common folder is configured
      correctly and then tries to enforce appropriate permissions.


    :param folder_path: Path where the common folder is located.
    :param common_group: Group name regarding the common folder.
      If not passed the existing group of the folder will be assumed to be the proper folder.
    """

    def __init__(self, folder_path: PosixPath, common_group: str = ""):
        """
        Initialize CommonFolder class.
        """

        if not isinstance(folder_path, PosixPath):
            raise TypeError(f"Expected PosixPath object instead of {type(folder_path)}")

        if not folder_path.exists():
            raise FileNotFoundError(
                "Folder is expected to be present when the class is initialized."
            )

        self.path: PosixPath = folder_path

        if common_group == "":
            # TODO: Add warning when logging gets added.
            self.group: str = self.path.group()
        else:
            self.group = common_group

        self.user: str = getpwuid(getuid()).pw_name

        # create logger
        logger = logging.getLogger("fcust")
        logger.setLevel(logging.DEBUG)
        # Create handlers
        sh = logging.StreamHandler()
        # TODO: make filename depend on day/time?
        logpath = Path("/tmp/fcust")
        logpath.mkdir(exist_ok=True)
        logpath = logpath.joinpath(self.user + ".log")
        fh = logging.FileHandler(str(logpath), mode="w")
        sh.setLevel(logging.DEBUG)
        fh.setLevel(logging.DEBUG)
        # Create formatters and add it to handlers
        format1 = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
        format2 = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        sh.setFormatter(format1)
        fh.setFormatter(format2)
        # Add handlers to the logger
        logger.addHandler(sh)
        logger.addHandler(fh)
        # add logger object to class
        self.logger: logging.Logger = logger

        logger.info(f"CommonFolder class instantiated for: {str(folder_path)}")

    def enforce_permissions(self):
        """
        We read the contents of a specified directory and enforce unix permissions.

        Files should have 664 permissions
        Folders should have 2775 permisions (ie also setguid bit)
        Group should be common golder's group.

        The function only changes permissions if the user is owner of the relevant resource.
        This is done to avoid the need for root access, but requires the function to be
        run by all the users sharing the common folder.
        """

        try:
            self.logger.info("Starting permissions enforcement")
            # Let's iterate over folders we find first - glob returns a generator!
            list1 = self.path.glob("**/*")
            for il in list1:
                pil = Path(il)

                # Fix group membership if needed
                if pil.group() != self.group and pil.owner() == self.user:
                    chown(pil, group=self.group)
                    self.logger.debug(f"Fixing group for {str(pil)}")

                # Check folder permissions and fix if needed
                if pil.is_dir():
                    perms: str = oct(pil.stat().st_mode)[-4:]
                    if perms != "2775" and pil.owner() == self.user:
                        pil.chmod(0o42775)
                        self.logger.debug(f"Fixing permissions for {str(pil)}")

                # Check folder permissions and fix if needed
                if pil.is_file():
                    perms: str = oct(pil.stat().st_mode)[-4:]
                    if perms != "0664" and pil.owner() == self.user:
                        pil.chmod(0o40664)
                        self.logger.debug(f"Fixing permissions for {str(pil)}")

        except Exception as exc:
            self.logger.critical(exc, exc_info=True)

        self.logger.info("Finished permissions enforcement")
