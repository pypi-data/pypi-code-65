from setuptools import setup


_readme = 'README.md'

_extras_path = 'extras'

with open(_extras_path+'/.env', 'r') as f:
    line = f.readline()
    if line.startswith('PACKAGE='):
        _package = line.splitlines()[0].split('=')[1].lower()

with open(_readme, 'r') as f:
    long_description = f.read()

required = []
with open(_extras_path+'/requirements.txt', 'r') as f:
    required = [line.splitlines()[0] for line in f]
# hack to handle diff between pip and conda 'redis' package name
if any('redis' in s for s in required):
    from sys import argv as sys_argv
    if 'conda' in sys_argv:
        for i,elt in enumerate(required):
            if 'redis' in elt:
                required[i] = required[i].replace('redis', 'redis-py')


_release = 'RELEASE'

with open(_release, 'r') as f:
    _version = f.readline().split()[0]

setup(
    name=_package,
    version=_version,
    author='Melchior du Lac, Joan Hérisson',
    author_email='joan.herisson@univ-evry.fr',
    description='BRSynth Utilities',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/brsynth/CRedisDict',
    packages=[_package],
    package_dir={_package: _package},
    include_package_data=True,
    install_requires=required,
    tests_require=required,
    test_suite='pytest',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.5',
)
