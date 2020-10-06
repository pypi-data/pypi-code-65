from structlog_ext_utils import __version__

from collections import OrderedDict

import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="structlog_ext_utils",
    version=f"{__version__}",
    author="alexandre menezes",
    author_email="alexandre.fmenezes@gmail.com",
    description="structlog extension utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="Apache-2.0",
    url="https://github.com/amenezes/structlog_ext_utils",
    packages=setuptools.find_packages(include=["structlog_ext_utils", "structlog_ext_utils.*"]),
    python_requires=">=3.6.0",
    project_urls=OrderedDict(
        (
            ("Documentation", "https://structlog_ext_utils.amenezes.net"),
            ("Code", "https://github.com/amenezes/structlog_ext_utils"),
            ("Issue tracker", "https://github.com/amenezes/structlog_ext_utils/issues"),
        )
    ),
    install_requires=["structlog<=20.1.0", "python-json-logger", "pendulum"],
    tests_require=[
        "pytest",
        "flake8",
        "pytest-cov",
        "pytest-mock",
        "isort",
        "black",
        "mypy",
        "tox",
        "codecov",
        "portray",
        "tox-asdf"
    ],
    extras_require={
        "docs": ["portray"],
        "all": ["structlog<=20.1.0", "python-json-logger", "portray"],
    },
    setup_requires=["setuptools>=38.6.0"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries",
    ],
)
