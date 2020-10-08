from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='plot_gsheets',
      version='0.4',
      description='plot gsheets by specifying columns',
      author='Ayush Saini',
      author_email='saini712@gmail.com',
      packages=['plot_gsheets'],
      include_package_data=True,
      install_requires=['google-api-python-client','google-auth-httplib2','google-auth-oauthlib','matplotlib'],
      long_description=long_description,
      long_description_content_type='text/markdown'
      )