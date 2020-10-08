from setuptools import setup

setup(
  name = 'gitpm',
  version = '0.1.0',
  description = 'Efficient multi git-repository project management.',
  long_description = 'Use gitpm to manage your local codebase.',

  classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',

    'License :: Free For Educational Use',
    'License :: Free For Home Use',
    'License :: Free for non-commercial use',

    'Programming Language :: Python :: 3.8',

    'Topic :: Software Development',
    'Topic :: Software Development :: Version Control',
    'Topic :: Software Development :: Version Control :: Git',
  ],

  keywords = 'git management repositories manager efficiency',
  url = 'http://github.com/finnmglas/gitPM',

  author = 'Finn M Glas',
  author_email = 'finn@finnmglas.com',

  license = 'MIT',
  packages = ['gitpm'],
  entry_points = {
    'console_scripts': ['gitpm=gitpm.command_line:main'],
  },

  install_requires = [
    'markdown',
  ],
  include_package_data=True,
  zip_safe = False
)
