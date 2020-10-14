from ftw.upgrade import UpgradeStep


class InstallFtwColorbox(UpgradeStep):
    """Install ftw.colorbox.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.ensure_profile_installed('profile-ftw.colorbox:default')
