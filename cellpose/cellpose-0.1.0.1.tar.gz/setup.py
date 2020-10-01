import setuptools
from setuptools import setup

install_deps = ['numpy', 'scipy', 'natsort',
                'tifffile', 'tqdm', 'numba',
                'mxnet_mkl', 'opencv-python-headless']

try:
    import mxnet as mx
    a = mx.nd.ones((2, 3))
    install_deps.remove('mxnet_mkl')
except:
    pass

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="cellpose",
    license="BSD",
    author="Marius Pachitariu and Carsen Stringer",
    author_email="stringerc@janelia.hhmi.org",
    description="anatomical segmentation algorithm",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MouseLand/cellpose",
    setup_requires=[
      'pytest-runner',
      'setuptools_scm',
    ],
    packages=setuptools.find_packages(),
    use_scm_version=True,
    install_requires = install_deps,
    tests_require=[
      'pytest',
      'pytest-qt',
    ],
    extras_require = {
      'docs': [
        'sphinx>=3.0',
        'sphinxcontrib-apidoc',
        'sphinx_rtd_theme',
      ],
      'gui': [
        'pyqtgraph==0.11.0rc0', 
        'pyqt5', 
        'google-cloud-storage'
        ]
    },
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ),
     entry_points = {
        'console_scripts': [
          'cellpose = cellpose.__main__:main']
     }
)
