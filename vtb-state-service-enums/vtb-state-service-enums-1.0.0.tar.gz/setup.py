from setuptools import setup, find_packages

"""
python setup.py sdist bdist_wheel
python -m twine upload --repository pypi dist/*
"""

setup(
    name='vtb-state-service-enums',
    version='1.0.0',
    packages=find_packages(exclude=['tests']),
    url='https://bitbucket.org/Michail_Shutov/state_service_enums',
    license='',
    author='Mikhail Shutov',
    author_email='michael-russ@yandex.ru',
    description='enums for VTB state service'
)
