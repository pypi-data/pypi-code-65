from setuptools import setup

setup(
    name='UTMDriver',
    version='v0.3-alpha',
    packages=['UTMDriver', 'UTMDriver.generic', 'UTMDriver.generic.helpers', 'UTMDriver.generic.queries',
              'UTMDriver.generic.queries.utm', 'UTMDriver.generic.queries.documents', 'UTMDriver.generic.documents',
              'UTMDriver.generic.documents.NATTN', 'UTMDriver.generic.documents.rests',
              'UTMDriver.generic.documents.tickets', 'UTMDriver.generic.documents.waybill'],
    url='https://github.com/maxpoint2point/UTMDriver',
    license='Apache-2.0 License',
    author='Максим',
    author_email='maxpoint2point@gmail.com',
    description='UTMDriver for EGAIS'
)
