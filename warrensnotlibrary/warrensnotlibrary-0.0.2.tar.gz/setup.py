from setuptools import setup, find_packages

classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

setup(
	name='warrensnotlibrary',
	version='0.0.2',
	description='stop.',
	long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
	url='',
	author='Warren Stevens',
	author_email='rathernottell@gmail.com',
	license='MIT',
	classifiers=classifiers,
	keywords='not',
	packages=find_packages(),
	install_requires=['']
)