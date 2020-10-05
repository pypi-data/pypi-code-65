from distutils.core import setup
setup(
  name = 'simscidapy',         # How you named your package folder (MyLib)
  packages = ['simscidapy'],   # Chose the same as "name"
  version = '1.0.0',      # Start with a small number and increase it with every change you make
  license='gpl-3.0',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Simple scientific data analysis in python. This package provides a compact and easy to use interface for the treatment and analysis of scientific data. It allows the user to forget about indices and lists and takes care of interpolation when dealing with unequally defined data.',   # Give a short description about your library
  author = 'David Wander',                   # Type in your name
  author_email = 'davidjwander@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/djwander/simscidapy',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/djwander/simscidapy/archive/v_001.tar.gz',    # I explain this later on
  keywords = ['numerics', 'scientific', 'data analysis','data treatment'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'numpy',
          'matplotlib',
          'scipy',
          'numba',
          'gwyfile'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Science/Research',      # Define that your audience are developers
    'Topic :: Scientific/Engineering :: Information Analysis',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)