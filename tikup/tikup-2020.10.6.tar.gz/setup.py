from setuptools import setup, find_packages
from os import path
from tikup.tikup import getVersion

here = path.abspath(path.dirname(__file__))

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='tikup',
    version=getVersion(),
    description='An auto downloader and uploader for TikTok videos.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Coloradohusky/TikUp',
    author='Coloradohusky',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'tikup = tikup.tikup:main',
        ],
    },
    python_requires='>=3.5, <4',
    install_requires=['internetarchive>=1.9.4', 'TikTokApi>=3.5.2', 'youtube-dl>=2020.09.20']
)
