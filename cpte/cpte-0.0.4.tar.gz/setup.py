from distutils.core import setup

setup(
    name='cpte',
    packages=['cpte'],  # this must be the same as the name above
    version='0.0.4',
    description='Set of classes for rapid development of Conan packages',
    author='Fluendo',
    author_email='mjimeno@fluendo.com',
    url='https://github.com/fluendo/conan_package_tools_extender',  # use the URL to the github repo
    download_url='https://github.com/fluendo/conan_package_tools_extender/tarball/0.0.4',
    keywords=['conan', 'builder'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
