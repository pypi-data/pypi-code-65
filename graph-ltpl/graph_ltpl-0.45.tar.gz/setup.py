import setuptools

"""
NOTE: This script is only used for package generation! Do not execute, unless intended package changes.

1. Package can be built with following command:
python3 setup.py sdist bdist_wheel

2a. Package on pypi.org can be updated with the following command:
sudo python3 -m twine upload --skip-existing dist/*

2b. Install locally only:
python3 -m pip install dist/xxxxxxx.whl
"""

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='graph_ltpl',
    version='0.45',
    author="Tim Stahl",
    author_email="stahl@ftm.mw.tum.de",
    description="Multilayer graph-based local trajectory planner.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=["*vp_qp*"]),
    install_requires=['numpy==1.18.1',
                      'matplotlib==3.3.1',
                      'scipy==1.3.3',
                      'python-igraph==0.8.2',
                      'trajectory_planning_helpers==0.71'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ])
