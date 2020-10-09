import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="data-struct",
    version="1.2.0",
    author="Eddie Breeg",
    license="GPLv3",
    author_email="eddiebreeg0@protonmail.com",
    description="A class to help you handling complex JSON-like objects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EddieBreeg/structLib",
    py_modules=['structLib'],
    package_dir={'': "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    # complete classifier list: https://pypi.org/classifiers/
    python_requires='>=3.8',
    install_requires=[
    ],
    extras_require={
        'dev': ["pytest>=6.0.1"],
    },
)
