""" setup.py created according to https://packaging.python.org/tutorials/packaging-projects """

import setuptools #type:ignore

setuptools.setup(
    name="qcaus",
    version="0.0.0",
    author="hashberg",
    author_email="sg495@users.noreply.github.com",
    description="A Python library for quantum causality.",
    url="https://github.com/hashberg-io/qcaus",
    packages=setuptools.find_packages(exclude=["test"]),
    classifiers=[ # see https://pypi.org/classifiers/
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Development Status :: 1 - Planning",
        "Natural Language :: English",
        "Typing :: Typed",
    ],
    package_data={"": [],
                  "qcaus": ["qcaus/py.typed"],
                 },
    install_requires=[
        "numpy",
    ],
    include_package_data=True
)
