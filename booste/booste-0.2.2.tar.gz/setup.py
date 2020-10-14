from distutils.core import setup
import setuptools
setup(
  name = 'booste',         # How you named your package folder (MyLib)
  packages = ['booste'],   # Chose the same as "name"
  version = '0.2.2',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'The booste package is a python client to interact with your machine learning models hosted on Booste',   # Give a short description about your library
  author = 'Erik Dunteman',                   # Type in your name
  author_email = 'erik@booste.io',      # Type in your E-Mail
  url = 'https://www.booste.io',   # Provide either the link to your github or to your website
  keywords = ['Booste client', 'API wrapper', 'Booste'],   # Keywords that define your package best
  setup_requires = ['wheel'],
  install_requires=[         # I get to this in a second
    'certifi',
    'chardet',
    'idna',
    'requests',
    'urllib3',
    'numpy'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
