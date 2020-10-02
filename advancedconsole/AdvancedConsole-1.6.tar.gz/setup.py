from distutils.core import setup
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
setup(name='AdvancedConsole',
      version='1.6',
      py_modules=['Advancedconsole'],
      install_requires=[
          'keyboard'
      ], classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
      ],url="https://github.com/jack-the-hack/AdvancedConsole",
      long_description=long_description,
      long_description_content_type='text/reStructredText',
      )
