from setuptools import setup

with open('README.md', 'r') as fh:
   long_description = fh.read()
setup(
    name='dupload',
    version='0.0.3',    
    description='Upload anywhere, at any time.',
    url='https://github.com/dwiftejb/dupload',
    author='DwifteJB',
    author_email='dwifte@icloud.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['dupload'],
    install_requires=['requests',
                      'bs4',                     
                      ],

    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.8',
    ],
)