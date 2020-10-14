from setuptools import setup

import versioneer

# See setup.cfg for configuration details

setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass()
)
