import os
from setuptools import setup

def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

from distutils.util import convert_path
main_ns = {}
ver_path = convert_path('ISReader/version.py')
with open(ver_path) as ver_file:
	exec(ver_file.read(), main_ns)

setup(
	name = "ISReader",
	version = main_ns['__version__'],
	
	packages=['ISReader'],

	package_dir={
		"ISReader": "ISReader"
	},

	author = "Initial State Technologies",
	author_email = "support@initialstate.com",
	description = ("Read data from the Initial State IoT platform"),
	license = "MIT",
	keywords = "logger,logstream,initial state",
	url = "https://www.initialstate.com",
	
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Topic :: Utilities",
		"License :: OSI Approved :: MIT License"
	]
)