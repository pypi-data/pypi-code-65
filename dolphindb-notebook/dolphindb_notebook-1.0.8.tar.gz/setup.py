"""Setup script for dolphindb_notebook package.
"""

import glob
from setuptools import setup

DISTNAME = 'dolphindb_notebook'
DESCRIPTION = 'A Jupyter Notebook Extension for DolphinDB.'
LONG_DESCRIPTION = open('README.md', 'r').read()
AUTHOR = 'DolphinDB, Inc.'
AUTHOR_EMAIL = 'support@dolphindb.com'
URL = 'https://www.dolphindb.com'
LICENSE = 'DolphinDB'
REQUIRES = [
    "jupyter_nbextensions_configurator",
    "widgetsnbextension",
    "metakernel", 
    "jupyter_client", 
    "ipykernel",
    "dolphindb",
    "tabulate",
    "matplotlib",
    "flask",
    "mplfinance"
]
INSTALL_REQUIRES = [
    "jupyter_nbextensions_configurator",
    "widgetsnbextension",
    "metakernel", 
    "jupyter_client", 
    "ipykernel",
    "dolphindb",
    "tabulate",
    "matplotlib",
    "flask",
    "mplfinance"
]
PACKAGES = [DISTNAME]
PACKAGE_DATA = {
    DISTNAME: ['*.m'] + glob.glob('%s/**/*.*' % DISTNAME)
}
DATA_FILES = [
    (
        'share/jupyter/kernels/dolphindb', 
        [
            '%s/kernel.json' % DISTNAME
        ]  + glob.glob('%s/images/*.png' % DISTNAME)
    ),
    (
        'share/jupyter/kernels/dolphindb', 
        [
            '%s/creds.py' % DISTNAME
        ]
    ),
    (
        'share/jupyter/nbextensions/dolphindb',
        [
            '%s/dolphindb_extension/main.js' % DISTNAME,
            '%s/dolphindb_extension/description.yaml' % DISTNAME
        ]
    )
]
CLASSIFIERS = """\
Intended Audience :: Science/Research
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: JavaScript
Topic :: Scientific/Engineering
Topic :: Software Development
"""


setup(
    name=DISTNAME,
    version='1.0.8',
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    packages=PACKAGES,
    package_data=PACKAGE_DATA,
    include_package_data=True,
    data_files=DATA_FILES,
    url=URL,
    download_url=URL,
    keywords=['IPython', 'Jupyter', 'notebook', 'DolphinDB'],
    license=LICENSE,
    platforms=["Any"],
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    requires=REQUIRES,
    install_requires=INSTALL_REQUIRES,
    zip_safe=False
 )