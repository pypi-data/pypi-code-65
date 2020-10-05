#!/usr/bin/env python3

from setuptools import setup

setup(
	name="pydan",
	version='2.1',
	description='Python3 Data Utils',
	author='Jose Biosca Martín',
	author_email='jbiosca@zone-sys.net',
	#url='https://zone-sys.net/',
	python_requires='>=3.6',
	#packages=["lib"],
	packages=["pydan"],
	package_dir={"pydan": "src"},
	#py_modules=['ivscript', 'jdata', 'josen', 'run']
	install_requires=[
		'setuptools',
		'setproctitle',
		'colored_traceback',
		'dicttoxml',
		'xmltodict',
		'ruamel.yaml',
	],
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		"License :: OSI Approved :: MIT License",
		#'Topic :: Software development',
	],
)
