import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "libkosciuszko",
    version="0.0.1",
    packages=['libkosciuszko'],
    package_dir={
        'libkosciuszko': 'src',
    },
    author="happy_shredder",
    author_email="contact@etage.io",
    description="Library for managing kosciuszko vaults",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.sr.ht/~happy_shredder",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Topic :: Security :: Cryptography",
    ],
    python_requires='>=3.7',
)
