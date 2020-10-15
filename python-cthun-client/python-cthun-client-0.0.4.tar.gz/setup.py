from setuptools import setup

setup(
    name='python-cthun-client',
    url='https://github.com/Jason916/python-cthun-client',
    version='0.0.4',
    description='test',
    author='Jason916',
    author_email='Jason1989Xu@gmail.com',
    packages=[
        'cthun_client',
    ],
    install_requires=[
        'requests==2.*'
    ],
    classifiers=[
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
    ],
    include_package_data=True
)
