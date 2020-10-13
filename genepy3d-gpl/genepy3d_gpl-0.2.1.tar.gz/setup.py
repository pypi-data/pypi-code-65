import pathlib
from setuptools import setup, find_namespace_packages

# The text of the README file
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

# Setup configuration
setup(
    name='genepy3d_gpl',
    version='0.2.1',
    description=(
      "GeNePy3D functions under GPL-like license"
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    author='genepy3d-team',
    url='https://gitlab.com/genepy3d/genepy3d-gpl',
    license="GPL",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    package_dir={'':'src'},
    packages=find_namespace_packages(where="src"),
    include_package_data=False,
    python_requires=">=3.6",
    install_requires=["genepy3d==0.2.1"]
)
