from setuptools import setup
with open('DESCRIPTION.txt') as file:
    long_description = file.read()
REQUIREMENTS=['mysql-connector-python~=8.0.21'],
setup(name="ConnectSQl",
      download_url="https://github.com/kailash1011/ConnectSQl/releases/tag/2.0",
      version='2.0',
      description="Connect Access & retrieve MYSQl databases.",
      url="https://github.com/kailash1011/ConnectSQl",
      author="Kailash Sharma",
      author_email="kailashps.1011@gmail.com",
      license="MIT",
      classifiers=['Programming Language :: Python :: 3.6'],
      long_description=long_description

      )
