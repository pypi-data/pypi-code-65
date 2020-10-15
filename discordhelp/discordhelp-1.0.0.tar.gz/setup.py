import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="discordhelp",
    version="1.0.0",
    author="Ashvin Ranjan",
    author_email="me@ash.vin",
    description="A library to help with discord.py",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ashvin-Ranjan/Discord-Helper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
          'discord.py'
    ],
    python_requires='>=3.6',
)