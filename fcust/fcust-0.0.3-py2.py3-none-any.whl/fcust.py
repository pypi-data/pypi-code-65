"""
Main module.
"""

from pathlib import PosixPath, Path
from shutil import chown


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

    def enforce_permissions(self):
        """
        We read the contents of a specified directory and enforce unix permissions.

        Files should have 664 permissions
        Folders should have 2775 permisions (ie also setguid bit)
        Group should be common golder's group.
        """

        # Let's iterate over folders we find first - glob returns a generator!
        list1 = self.path.glob("**/*")
        for il in list1:
            pil = Path(il)

            # Fix group membership if needed
            if pil.group() != self.group:
                chown(pil, group=self.group)

            # Check folder permissions and fix if needed
            if pil.is_dir():
                perms: str = oct(pil.stat().st_mode)[-4:]
                if perms != "2775":
                    pil.chmod(0o42775)

            # Check folder permissions and fix if needed
            if pil.is_file():
                perms: str = oct(pil.stat().st_mode)[-4:]
                if perms != "0664":
                    pil.chmod(0o40664)
