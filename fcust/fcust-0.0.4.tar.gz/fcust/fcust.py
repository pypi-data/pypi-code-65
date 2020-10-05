"""
Main module.
"""

from pathlib import PosixPath, Path
from shutil import chown
from pwd import getpwuid
from os import getuid


class CommonFolder:
    """

    Main class regarding management of a folder that is commonly used across many users.

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

        # Let's iterate over folders we find first - glob returns a generator!
        list1 = self.path.glob("**/*")
        for il in list1:
            pil = Path(il)

            # Fix group membership if needed
            if pil.group() != self.group and pil.owner() == self.user:
                chown(pil, group=self.group)

            # Check folder permissions and fix if needed
            if pil.is_dir():
                perms: str = oct(pil.stat().st_mode)[-4:]
                if perms != "2775" and pil.owner() == self.user:
                    pil.chmod(0o42775)

            # Check folder permissions and fix if needed
            if pil.is_file():
                perms: str = oct(pil.stat().st_mode)[-4:]
                if perms != "0664" and pil.owner() == self.user:
                    pil.chmod(0o40664)
