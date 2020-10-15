"""
Flask-Tus-Cont
-------------

Implements the tus.io server-side file-upload protocol
visit http://tus.io for more information

"""
from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='Flask-Tus-Cont',
    version='0.6.1',
    url='https://github.com/gnubyte/Flask-Tus',
    license='MIT',
    author='Matt Hoskins',
    author_email='phastings@openmobo.com',
    description='TUS protocol implementation',
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=['flask_tus_cont'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
		'Redis'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
