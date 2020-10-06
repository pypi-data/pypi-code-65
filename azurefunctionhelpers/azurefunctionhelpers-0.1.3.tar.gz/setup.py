from setuptools import setup, find_packages


setup(
    name='azurefunctionhelpers',
    version='0.1.3',
    description='Library of helpers for use with Azure Functions',
    url='https://github.com/AirWalk-Digital/azure_function_helpers',
    author='AirWalk Consulting',
    author_email='info@airwalkconsulting.com',
    license='MIT',
    packages = find_packages(where='azurefunctionhelpers'),
    install_requires=['elastic-apm==5.9.0']
)

