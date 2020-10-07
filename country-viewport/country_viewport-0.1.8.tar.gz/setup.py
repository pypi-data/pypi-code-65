import pathlib
import setuptools

from distutils.core import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name='country_viewport',
    packages=['country_viewport'],
    package_data={'country_viewport': ['viewports.csv']},
    include_package_data=True,
    version='0.1.8',
    license='MIT',
    description='Extract viewports from country codes, without the need of relying on Google APIs.',
    long_description=README,
    long_description_content_type="text/markdown",
    author='YTEC',
    author_email='alvin@ytec.nl',
    url='https://ytec.nl/',
    keywords=['viewport', 'country'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
