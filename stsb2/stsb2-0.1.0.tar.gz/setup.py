from setuptools import setup

setup(
    name="stsb2",
    version="0.1.0",
    description="structural time series grammar and models",
    url="https://gitlab.com/daviddewhurst/stsb2",
    author="David Rushing Dewhurst",
    author_email="drd@davidrushingdewhurst.com",
    license="GNU General Public License v2 (GPLv2)",
    packages=['stsb2'],
    install_requires=[
        'numpy', 'scipy',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Office/Business :: Financial :: Investment'
    ]
)
