# A Python file for setuptools.

# Egg: importable methods for builds on Python packages.
#
# Update metadata and publish a new build with source distribution.
# python setup.py sdist upload
# twine upload dist/*

# Wheel: installation method for builds on Python packages.
#
# python setup.py bdist_wheel

# Development Mode
# python setup.py develop

from setuptools import setup, find_packages
import versioneer

# Get the long description from the README file
with open('README.rst') as f:
    readme = f.read()

COMMAND_NAME = 'oboyo'

setup(

    # This is the name of your project. The first time you publish this
    # package, this name will be registered for you. It will determine how
    # users can install this project, e.g.:
    #
    # $ pip install sampleproject
    #
    # And where it will live on PyPI: https://pypi.org/project/sampleproject/
    #
    # There are some restrictions on what makes a valid project name
    # specification here:
    # https://packaging.python.org/specifications/core-metadata/#name
    name=COMMAND_NAME,


    # -- Project information -----------------------------------------------------

    # Versions should comply with PEP 440:
    # https://www.python.org/dev/peps/pep-0440/
    #
    # For a discussion on single-sourcing the version across setup.py and the
    # project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=versioneer.get_version(),

    # This is a one-line description or tagline of what your project does. This
    # corresponds to the "Summary" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#summary
    description='A test package',

    # This is an optional longer description of your project that represents
    # the body of text which users will see when they visit PyPI.
    #
    # Often, this is the same as your README, so you can just read it in from
    # that file directly (as we have already done above)
    #
    # This field corresponds to the "Description" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#description-optional
    long_description=readme,
    long_description_content_type='text/x-rst',

    # This should be a valid link to your project's main homepage.
    #
    # This field corresponds to the "Home-Page" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#home-page-optional
    url='https://github.com/coatk1/playground',

    # This should be your name or the name of the organization which owns the
    # project.
    author='Corey Atkins',

    # This should be a valid email address corresponding to the author listed
    # above.
    author_email='coatk1@umbc.edu',

    # Maintainer
    maintainer='Corey Atkins',
    maintainer_email='coatk1@umbc.edu',

    # Use license in MANIFEST.in
    # license='MIT',
    # license_file=LICENSE.md,

    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[

        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # The operating system that is used
        'Environment :: Win32 (MS Windows)',
        'Operating System :: Microsoft :: Windows',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Topic :: Software Development :: Libraries :: Python Modules',

        # Pick your license as you wish
        # 'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        # These classifiers are *not* checked by 'pip install'. See instead
        # 'python_requires' below.
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    #
    # Note that this is a string of words separated by whitespace, not a list.
    keywords=[

    ],

    # -- Package setup -----------------------------------------------------------

    # When your source code is in a subdirectory under the project root, e.g.
    # `src/`, it is necessary to specify the `package_dir` argument.
    package_dir={
        'oboyo': 'oboyo'
    },

    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    packages=find_packages('.'),
    # packages=['oboyo'],

    # Specify which Python versions you support. In contrast to the
    # 'Programming Language' classifiers above, 'pip install' will check this
    # and refuse to install the project if the version does not match. If you
    # do not support Python 2, you can simplify this to '>=3.5' or similar, see
    # https://packaging.python.org/guides/distributing-packages-using-setuptools/#python-requires
    python_requires='>=3.6',
    setup_requires=[
        'pytest-runner',
    ],

    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'click >= 6',
        'flake8',
        'pydocstyle'
    ],
    include_package_data=True,
    # test_suite='pytest',
    tests_require=[
        'pytest-cov'
    ],


    # -- Executable scripts ------------------------------------------------------

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `sample` which
    # executes the function `main` from this package when invoked:
    entry_points={
        'console_scripts': [
            '{} = oboyo.cli:cli'.format(COMMAND_NAME)
        ],
    },


    # -- Additional URLs ---------------------------------------------------------

    # List additional URLs that are relevant to your project as a dict.
    #
    # This field corresponds to the "Project-URL" metadata fields:
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    #
    # Examples listed include a pattern for specifying where the package tracks
    # issues, where the source is hosted, where to say thanks to the package
    # maintainers, and where to support the project financially. The key is
    # what's used to render the link text on PyPI.
    project_urls={
    'Source': 'https://github.com/coatk1/playground/',
    'Tracker': 'https://github.com/coatk1/playground/issues',
    },
)
