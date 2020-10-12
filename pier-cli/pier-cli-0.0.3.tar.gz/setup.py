from setuptools import find_packages, setup


with open("VERSION", "r") as fh:
    __version__ = fh.read().strip()


with open("README.md", "r") as fh:
    __long_description__ = fh.read()


setup(
    name="pier-cli",
    version=__version__,
    author="Marten Sies",
    description="pier-cli is a development tool that provides an easy way to deploy your local images to Kubernetes",
    long_description=__long_description__,
    long_description_content_type="text/markdown",
    provides=[
        'pier',
    ],
    entry_points={
        'console_scripts': [
            '%s=%s.cli.run:cli' % ('pier', 'pier_cli')
        ],
    },
    install_requires=['docker', 'kubernetes', 'fire', 'tabulate'],
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Environment :: Console",
    ],
    python_requires='>=3.6',
)