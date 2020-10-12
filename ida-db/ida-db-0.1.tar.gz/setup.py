from setuptools import setup, find_packages

setup(name='ida-db',
      version='0.1',
      url='https://github.com/project-ida/ida-db',
      license='MIT',
      author='Project Ida',
      author_email='info@project-ida.org',
      description='Interface to Timescale PostgreSQL database',
      packages=find_packages(),
      install_requires=['psycopg2','numpy'],
      zip_safe=False)
