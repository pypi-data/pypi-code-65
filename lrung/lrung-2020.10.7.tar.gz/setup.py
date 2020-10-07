
from distutils.core import setup
from setuptools import find_packages
 
setup(name = 'lrung',     #  
      version = '2020.10.07',  #  
      description = 'lru ng',
      long_description = '', 
      author = 'frankli',
      author_email = '',
      url = '',
      license = '',
      install_requires = [],
      classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities'
      ],
      keywords = '',
      packages = find_packages('src'),  #  
      package_dir = {'':'src'},         # 
      include_package_data = True,
)