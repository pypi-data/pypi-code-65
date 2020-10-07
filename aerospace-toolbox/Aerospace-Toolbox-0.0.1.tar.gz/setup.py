#  setup.py
#  setup.py
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = 'Aerospace-Toolbox',
    packages = setuptools.find_packages(),
    version = 'v0.0.1',  # Ideally should be same as your GitHub release tag varsion
    description = 'Aerospace Toolbox - A Python Package For Aeronautical & Astronautical Engineers',
    author = 'A. H. Khodabakhsh',
    author_email = 'a.h.khodabakhsh@gmail.com',
    url = 'https://github.com/ahkhodabakhsh/Aerospace-Toolbox',
    download_url = 'https://github.com/ahkhodabakhsh/Aerospace-Toolbox/archive/v0.0.1.tar.gz',
    keywords = ['Aerospace', 'Flight Dynamics', 'Aerodynamics', 'Coordiante Transformation'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
