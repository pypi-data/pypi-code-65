from distutils.core import setup
setup(
  name = 'pykgr',
  packages = ['pykgr'],
  version = '0.1',
  description = 'A never root software builder, like nix for poor people',
  author = 'Dylan Holland',
  author_email = 'salinson1138@gmail.com',
  url = 'https://github.com/DylanEHolland/pykgr',
  download_url = 'https://github.com/DylanEHolland/pykgr/archive/0.1.tar.gz',
  keywords = ['SOFTWARE',"PACKAGER"],
  install_requires=[ 
          'argparse',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha', # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
    'Topic :: Software Development :: Build Tools',
    'Programming Language :: Python :: 3',
  ],
)