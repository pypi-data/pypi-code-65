from pathlib import Path
import re

from setuptools import setup, find_packages


def get_version():
    text = Path('twissgrid/__init__.py').read_text()
    return re.findall("^__version__ = '(.+)'$", text, flags=re.M)[0]


setup(
    name='TwissGrid',
    version=get_version(),
    description='Visualize Twiss parameters for one- or two-dimensional grid scan of lattice parameters.',
    long_description=Path('README.md').read_text(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
    keywords=['MADX', 'lattice', 'Twiss', 'parameter scan', 'visualization'],
    url='https://gitlab.com/Dominik1123/twissgrid',
    author='Dominik Vilsmeier',
    author_email='d.vilsmeier@gsi.de',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'cpymad',
        'matplotlib',
        'numpy',
    ],
    python_requires='>=3.7',
)
