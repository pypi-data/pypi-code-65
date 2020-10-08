import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
        name="camelot_frs",
        version="0.0.2",
        author="Tomer Altman",
        author_email="camelot@me.tomeraltman.net",
        description="A frame representation system in Python.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://bitbucket.org/tomeraltman/camelot-frs/",
        packages=['camelot_frs'],
        install_requires=[
            'scipy',
        ],
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
            "Operating System :: OS Independent",
        ],
        python_requires='>=3.6',
)
