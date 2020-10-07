import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lumaserv-domain-api",
    version="0.0.7",
    author="Adrijan Bajrami",
    author_email="abajrami@everhype-systems.eu",
    description="API Wrapper for LumaServ Domain API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EverHype-Systems/lumaserv-domain-api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
