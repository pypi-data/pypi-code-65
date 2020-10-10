from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()


setup_args = dict(
    name='common_interfaces',
    version='0.1.2',
    description='Useful tools to work with ETL Redis config in Python',
    long_description_content_type="text/markdown",
    long_description=README,
    license='MIT',
    packages=find_packages(),
    author='Rajendran',
    author_email='rajumonpk@hotmail.com',
    url='https://github.com/rajumonpk/common_interfaces',
    download_url='https://pypi.org/project/common_interfaces/'
)

install_requires = [
    'redis==3.5.3',
    'rq'
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
