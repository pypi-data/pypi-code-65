import pathlib
from setuptools import setup
import among_us_parser

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="among-us-parser",
    version=among_us_parser.__version__,
    description="A parser for the game among us, that the games network packets",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/RedstoneMedia/among-us-parser-python",
    author="RedstoneMedia",
    keywords="parser network packets among-us AmongUs",
    license="GNU General Public License v3.0",
    packages=["among_us_parser"],
    include_package_data=True,
    install_requires=["python-pcapng>=1.0"],
)