import setuptools
from setuptools import setup


def find_pytket_subpackages():
    locations = [("pytket", "pytket"), ("pytket/backends", "pytket.backends")]
    pkg_list = []

    for location, prefix in locations:
        pkg_list += list(
            map(
                lambda package_name: "{}.{}".format(prefix, package_name),
                setuptools.find_packages(where=location),
            )
        )

    return pkg_list


version = {}
with open("_version.py") as fp:
    exec(fp.read(), version)

setup(
    name="pytket-ionq",
    version=version["__version__"],
    author="Alexander Cowtan",
    author_email="alexander.cowtan@cambridgequantum.com",
    python_requires=">=3.6",
    url="https://github.com/CQCL/pytket",
    description="Extension for pytket, providing access to AQT backends",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="CQC Non-Commercial Use Software Licence",
    packages=find_pytket_subpackages(),
    include_package_data=True,
    install_requires=["pytket ~= 0.6", "requests ~= 2.22"],
    classifiers=[
        "Environment :: Console",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: Other/Proprietary License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering",
    ],
    zip_safe=False,
)
