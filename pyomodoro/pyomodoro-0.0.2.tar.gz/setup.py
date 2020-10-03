import setuptools

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

readme = ''
with open('README.md') as f:
    readme = f.read()

setuptools.setup(
    name='pyomodoro',
    author='Ted Tramonte',
    url='https://gitlab.com/tedtramonte/pyomodoro',
    project_urls={
        "Issue tracker": "https://gitlab.com/tedtramonte/pyomodoro/issues",
    },
    use_scm_version=True,
    packages=setuptools.find_packages(),
    license='MIT',
    description='An easy to use CLI for the Pomodoro Technique.',
    long_description=readme,
    long_description_content_type="text/markdown",
    setup_requires=[
        'setuptools_scm'
    ],
    include_package_data=True,
    install_requires=requirements,
    entry_points='''
    [console_scripts]
    pom=pyomodoro.cli:start
    pyomodoro=pyomodoro.cli:start
    ''',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Education',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Education',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Other/Nonlisted Topic',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities',
    ]
)
