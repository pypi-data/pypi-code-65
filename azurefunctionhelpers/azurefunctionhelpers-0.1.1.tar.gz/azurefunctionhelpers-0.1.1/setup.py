from setuptools import setup


setup(
    name='azurefunctionhelpers',
    version='0.1.1',
    description='Library of helpers for use with Azure Functions',
    url='https://github.com/AirWalk-Digital/azure_function_helpers',
    author='AirWalk Consulting',
    author_email='info@airwalkconsulting.com',
    license='MIT',
    packages=['azurefunctionhelpers'],
    install_requires=['elastic-apm==5.9.0']
)
