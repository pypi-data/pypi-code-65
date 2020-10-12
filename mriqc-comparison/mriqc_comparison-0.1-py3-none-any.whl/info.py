__version__ = "0.1"
__author__ = "Pablo Velasco"
__author_email__ = "pablo.velasco@nyu.edu"
__url__ = "https://github.com/cbinyu/mriqc_comparison"
__packagename__ = 'mriqc_comparison'
__description__ = "Compares MRIQC IQMs"
__license__ = "MIT"
__longdesc__ = """Tool to compare MRIQC Image Quality Metrics (IQMs) across BIDS projects, labs, centers, etc."""

CLASSIFIERS = [
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Topic :: Scientific/Engineering'
]

PYTHON_REQUIRES = ">=3.6"

REQUIRES = [
    'pandas >= 0.25.0',
    'numpy >= 1.17.1',
    'mriqc >= 0.15',
]

TESTS_REQUIRES = [
    'pytest'
]

EXTRA_REQUIRES = {
    'tests': TESTS_REQUIRES,
}

# Flatten the lists
EXTRA_REQUIRES['all'] = sum(EXTRA_REQUIRES.values(), [])
