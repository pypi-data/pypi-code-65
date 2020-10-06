from distutils.core import setup
setup(
  name = 'shortuid',
  packages = ['shortuid'],
  version = '0.0.1', 
  license='MIT',
  description = 'Mini package for generating fairly unique but short IDs', 
  author = 'Abdulhakeem Mustapha',                   # Type in your name
  author_email = 'abdulhakeemmustapha@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/aamustapha/short-uid',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/aamustapha/short-uid/archive/v_001.tar.gz',    # I explain this later on
  keywords = ['UUID', 'UUID indexing', 'short uuid', 'short-uid'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          
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