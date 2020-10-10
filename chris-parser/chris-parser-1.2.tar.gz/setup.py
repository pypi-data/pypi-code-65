import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="chris-parser",
    version="1.2",
    author="Morgan Arnold",
    author_email="morgan.r.arnold@outlook.com",
    description="A parser for the .chris file type.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CrashAndSideburns/CHRIS-Parser",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Natural Language :: English"
    ],
    python_requires='>=3.6'
)