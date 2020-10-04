from setuptools import find_packages, setup


def readme():
    with open('README.md') as f:
        return f.read()


if __name__ == '__main__':
    setup(
        name='humble-tools',
        description='Humble Tools',
        long_description=readme(),
        author="Roland von Ohlen",
        author_email="work@rvo.name",
        license='proprietary',
        url='',
        scripts=[],
        package_dir={'': 'src'},
        packages=find_packages('src'),
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        entry_points={
            'console_scripts': [
                'htools=humble_tools.cli:main',
            ],
            'toolz_plugins': [
                'make = humble_tools_make:make'
            ]
        },
        include_package_data=True,
        use_scm_version=True,
        extras_require={
            'develop': [
                'pylint==2.3.1',
                'pytest==4.4.1',
                'pytest-cov==2.7.1',
                'pytest-mock==1.10.4',
                'pytest-freezegun==0.3.0.post1',
                'git-pylint-commit-hook==2.5.1',
                'setuptools_scm==3.2.0',
            ]
        },
        install_requires=[
            'click==7.1.2',
            'inotify==0.2.10',
        ],
        zip_safe=True
    )
