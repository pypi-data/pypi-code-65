from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="santa-7imbrook",
    version="0.1",
    author="Michael Timbrook",
    author_email="timbrook480@gmail.com",
    description="A secret santa matcher",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.6',
    entry_points="""
        [console_scripts]
        santa=santa:main
    """,
)