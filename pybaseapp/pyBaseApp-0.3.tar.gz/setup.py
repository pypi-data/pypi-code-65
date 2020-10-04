# from distutils.core import setup
# setup(
#   name = 'pyBaseApp',         # How you named your package folder (MyLib)
#   packages = ['pyBaseApp.applauncher','pyBaseApp.package'],   # Chose the same as "name"
#   version = '0.2',      # Start with a small number and increase it with every change you make
#   license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
#   description = 'Tools to define a standard way to launch and package python application',   # Give a short description about your library
#   author = '20centCroak',                   # Type in your name
#   author_email = 'vpaveau@outlook.com',      # Type in your E-Mail
#   url = 'https://github.com/20centcroak/pyBaseApp',   # Provide either the link to your github or to your website
#   download_url = 'https://github.com/20centcroak/pyBaseApp/archive/0.2.tar.gz',    # I explain this later on
#   keywords = ['LAUNCHER', 'PACKAGER', 'LAUNCH', 'PACKAGE', 'STANDARD', 'LOGGER', 'BASIC', 'APP'],   # Keywords that define your package best
#   install_requires=[            # I get to this in a second
#           'pyyaml',
#           'pyinstaller'
#       ],
#   classifiers=[
#     'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
#     'Intended Audience :: Developers',      # Define that your audience are developers
#     'Topic :: Software Development :: Build Tools',
#     'License :: OSI Approved :: MIT License',   # Again, pick a license
#     'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
#     'Programming Language :: Python :: 3.4',
#     'Programming Language :: Python :: 3.5',
#     'Programming Language :: Python :: 3.6',
#   ],
# )

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyBaseApp", 
    version="0.3",
    author="20centCroal",
    author_email="",
    description="Standard app configuration and packaging",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/20centcroak/pyBaseApp",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)