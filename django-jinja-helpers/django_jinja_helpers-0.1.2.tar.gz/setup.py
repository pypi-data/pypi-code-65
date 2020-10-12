import os
from setuptools import setup, find_packages
import django_jinja_helpers as app

install_requires = [
    'django >= 2.0',
    'django-crispy-forms>=1.7.2',
    'django-jinja>=2.5.0',
    'django-webpack-loader>=0.7.0 ',
]


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''

setup(
    name='django_jinja_helpers',
    version=app.__version__,
    description='Helpers for using django-jinja',
    long_description=read('README.rst'),
    license='The MIT License',
    platforms=['OS Independent'],
    keywords='django',
    author='Enrico Barzetti',
    author_email='enricobarzetti@gmail.com',
    url='https://github.com/enricobarzetti/django_jinja_helpers',
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
)
