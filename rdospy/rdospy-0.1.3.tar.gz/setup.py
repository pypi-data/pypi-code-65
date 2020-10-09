from setuptools import setup

setup(
   name='rdospy',
   version='0.1.3',
   author='Julien DAVID & Ismail MOUMNI',
   author_email='ism.moumni@gmail.com',
   url='http://pypi.python.org/pypi/RDOS-PYTHON/',
   description='RDOS PYTHON API',
   scripts=['client.py'],
   license='MIT',
   long_description=open('README.md').read(),
   python_requires='>=3.6'
)
