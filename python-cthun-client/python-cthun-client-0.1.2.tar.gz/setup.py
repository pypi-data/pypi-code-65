from setuptools import setup, find_packages

setup(
    name='python-cthun-client',
    url='https://github.com/Jason916/python-cthun-client',
    version='0.1.2',
    description='test',
    author='Jason916',
    author_email='Jason1989Xu@gmail.com',
    packages=find_packages(),
    install_requires=[
        'requests==2.*'
    ],
    classifiers=[
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
    ],
    include_package_data=True
)
