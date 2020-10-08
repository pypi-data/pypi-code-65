import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="onedrive-ignore",
    version="0.0.4",
    author="Fernando Balandran",
    author_email="fernandobe+git@protonmail.com",
    description="OneDrive ignore files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kodaman2/OneDriveIgnore",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            # command = package.module:function
            'onedrive = onedriveignore.one_drive_ignore:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)