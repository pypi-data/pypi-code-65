from pathlib import Path
from setuptools import setup


def get_long_description() -> str:
    return Path("README.md").read_text(encoding="utf8")


setup(
    name="snapwell",
    version="1.0.0",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    packages=["snapwell"],
    install_requires=["libecl", "equinor-libres"],
    entry_points={
        "console_scripts": [
            "snapwell=snapwell.snapwell_main:main",
        ]
    },
)
