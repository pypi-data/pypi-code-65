from distutils.core import setup
setup(
  name = 'imascii',        
  packages = ['imascii'],  
  version = '0.1',    
  license='MIT', 
  description = 'Converts image to ASCII pattern',  
  author = 'Ashutosh Jha',        
  author_email = 'aj97389@gmail.com', 
  url = 'https://github.com/user/mornville',  
  download_url = 'https://github.com/mornville/Imascii-py/archive/v_01.tar.gz',  
  keywords = ['ASCII', 'IMAGE', 'PATTERN', 'CONVERSION'],   
  install_requires=[
          'PIL',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha', 
    'Intended Audience :: Developers',   
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3', 
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)