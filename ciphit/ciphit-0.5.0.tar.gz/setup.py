import setuptools


with open('README.md', 'r') as readme_fp:
    long_description = readme_fp.read()

with open('requirements.txt', 'r') as req_fp:
    required_libs = req_fp.readlines()


setuptools.setup(
    name='ciphit',
    scripts=['ciphit/__main__.py'],
    description='ciphit is a cryptography CLI-tool',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='0.5.0',
    author='Sagar Kumar',
    license='MIT',
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=setuptools.find_packages(exclude=['install.sh']),
    install_requires=required_libs,
    url='https://github.com/sgrkmr/ciphit',
    keywords='cli commandline user-interface ui cryptography',
    python_requires='>=3.7',
    entry_points={
    'console_scripts': [
        'ciphit = ciphit.__main__:main',
        ],
    },
)
