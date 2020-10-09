from distutils.core import setup
setup(
  name = 'Phygital_v0',         # How you named your package folder (MyLib)
  packages = ['Phygital_v0'],   # Chose the same as "name"
  version = '0.4',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'This is the Lib to work on Python & Robotics projects',   # Give a short description about your library
  author = 'ME',                   # Type in your name
  author_email = 'renuka.angole@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/RenukaAngole1/Phygital_V0',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/RenukaAngole1/Phygital_V0/archive/0.4.tar.gz',    # I explain this later on
  keywords = ['Robotics', 'Sensors', 'Motors'],   # Keywords that define your package best
  install_requires=[ 'pyserial' ,'requests'          # I get to this in a second
          
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)