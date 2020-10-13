from setuptools import setup
__project__ = "Database-by-ike-welborn"
__version__ = "1.0.1"
__description__ = "a Python for making data programming esier"
__packages__ = ["data"]
__author__ = "Ike Welborn"
__author_email__ = "ike.welborn@gmail.com"
__requires__ = ["random"]
setup(
    name = __project__,
    version = __version__,
    description = __description__,
    packages = __packages__,
    author = __author__,
    author_email = __author_email__,
    requires = __requires__,
)
