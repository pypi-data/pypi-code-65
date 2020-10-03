import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "kosciuszko-utils",
    version="0.2.0",
    packages=['kosciuszko', 'kosciuszko_new', 'kosciuszko_extract', 'kosciuszko_extract_file', 'kosciuszko_list', 'kosciuszko_addfile'],
    package_dir={
        'kosciuszko': 'src/kosciuszko',
        'kosciuszko_new': 'src/new',
        'kosciuszko_extract': 'src/extract',
        'kosciuszko_extract_file': 'src/extract_file',
        'kosciuszko_list': 'src/list',
        'kosciuszko_addfile': 'src/addfile',
    },
    url="https://git.sr.ht/~happy_shredder/kosciuszko-utils",
    author="happy_shredder",
    author_email="contact@etage.io",
    description="Library for managing kosciuszko vaults",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Topic :: Security :: Cryptography",
        "Intended Audience :: End Users/Desktop",
        "Environment :: Console",
        "Development Status :: 3 - Alpha"
    ],
    install_requires=['libkosciuszko'],
    python_requires='>=3.7',
    entry_points={
        'console_scripts': ['kosciuszko=kosciuszko.__init__:main', 'kosciuszko-new=kosciuszko_new.__init__:main', 'kosciuszko-extract=kosciuszko_extract.__init__:main', 'kosciuszko-extract-file=kosciuszko_extract_file.__init__:main', 'kosciuszko-list=kosciuszko_list.__init__:main', 'kosciuszko-addfile=kosciuszko_addfile.__init__:main'],
        }
)
