from distutils.core import setup
setup(
  name = 'siro',
  packages = ['siro'],
  version = '0.1',
  license='MIT',
  description = 'This is a package for controlling the SIRO SmartHome Devices like rollers.',
  author = 'Felix Arnold',
  author_email = 'moin@felix-arnold.dev',      # Type in your E-Mail
  url = 'https://github.com/fear/siro',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/fear/siro/archive/0.1.tar.gz',    # I explain this later on
  keywords = ['SmartHome', 'Siro', 'roller', 'home assistant'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'asyncio',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)
