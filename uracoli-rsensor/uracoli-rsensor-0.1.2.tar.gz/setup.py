from __future__ import print_function
from setuptools import setup
from rsensor import __version__

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(name = 'uracoli-rsensor',
      version = __version__,
      description = 'A sensor logger framework for the uracoli rsensor firmware',
      long_description = long_description,
      long_description_content_type="text/markdown",
      maintainer = "Axel Wachtler",
      maintainer_email = "axel@uracoli.de",
      packages = ['rsensor',
                  'rsensor.logger',
                  'rsensor.webapp',
                  'rsensor.database',
                  'rsensor.testapp'],
      #package_dir={'rsensor': 'src/mypkg'},
      package_data={'rsensor': ['data/*.yml', 'data/rsensor.service']},

      #scripts = ['rsensor_logger.py', 'rsensor_server.py' ],
      #data_files = rsensor_data,
      install_requires = ['paho-mqtt', 'pyyaml', 'pymysql'],



      #data_files = [('.' , ['README.md', 'example.yml', 'rsensor/database/schema.yml'])],
      #include_package_data=True,
      license = "BSD",
      entry_points={
        'console_scripts':
            [
             'mqtt_to_db = rsensor.database.mqtt_to_db:main',
             'rinfo = rsensor:info',
             'rs_testgen = rsensor.testapp.rsensor_testgen:main' 
        ],}
      )
