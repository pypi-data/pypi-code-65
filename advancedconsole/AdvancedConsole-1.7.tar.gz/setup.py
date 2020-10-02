import setuptools
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
setuptools.setup(name='AdvancedConsole',
      version='1.7',
      py_modules=['Advancedconsole'],
      author="Donnie Jack Baldyga",
      install_requires=[
          'keyboard'
      ], classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
      ],
      url="https://github.com/jack-the-hack/AdvancedConsole",
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=setuptools.find_packages(),
      )
