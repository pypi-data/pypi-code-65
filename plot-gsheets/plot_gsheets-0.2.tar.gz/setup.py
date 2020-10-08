from setuptools import setup

setup(name='plot_gsheets',
      version='0.2',
      description='plot gsheets by specifying columns',
      author='Ayush Saini',
      author_email='saini712@gmail.com',
      packages=['plot_gsheets'],
      include_package_data=True,
      install_requires=[
     'google-api-python-client','google-auth-httplib2','google-auth-oauthlib','matplotlib'
      ],
      )