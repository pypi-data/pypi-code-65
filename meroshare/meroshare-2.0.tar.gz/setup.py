from distutils.core import setup
setup(
  name = 'meroshare',
  packages = ['meroshare'],
  entry_points = {
    'console_scripts': ['meroshare=meroshare.command_line:main']
  },
  version = '2.0', 
  license='MIT', 
  description = 'A python package to interact with meroshare', 
  author = 'Saurav Pathak', 
  author_email = 'saurab.pathak.0@gmail.com', 
  url = 'https://gitlab.com/saurab.pathak.0/meroshare.git',
  download_url = 'https://gitlab.com/saurab.pathak.0/meroshare/-/archive/v2.0/meroshare-v2.0.tar.gz',
  keywords = ['nepal', 'meroshareapi', 'stockmarketAPI'],
  install_requires=['requests', 'prettytable'],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',      #Specify which python versions that you want to support
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)
