from setuptools import setup
setup(
    name='kafka-connect-python-helper',
    version='0.0.1',
    description='Toolset for Kafka Connect REST API',
    url='https://github.com/MrMarshall/kafka-connect-python-helper',
    author='Marcel Renders',
    license='MIT',
    packages=['connect_helper'],
    install_requires=[
        'requests (>=2.24.0)',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
    ],
)