from distutils.core import setup

setup(
  name = 'PyDoser',        
  packages = ['PyDoser'],  
  version = '0.2',      
  license='MIT',     
  description = 'Python 3 app for testing security side of your web apps. HTTP DoS tool.',  
  author = 'Dominon12',              
  author_email = 'youneedmax@gmail.com',     
  url = 'https://github.com/dominon12/PyDoser',   
  download_url = 'https://github.com/dominon12/PyDoser/archive/v_02.tar.gz',   
  keywords = ['DoS', 'DDoS', 'security', 'education'], 
  install_requires=[         
          'requests',
          'fake_headers',
          'argparse'
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8'
  ],
)