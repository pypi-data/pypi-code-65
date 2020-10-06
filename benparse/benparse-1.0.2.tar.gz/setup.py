import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='benparse',
    version='1.0.2',
    author='Adralioh',
    description='Bencode parser',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/adralioh/benparse',
    project_urls={
        'Documentation': 'https://adralioh.gitlab.io/benparse'
    },
    packages=setuptools.find_packages(),
    package_data={
        '': ['py.typed']
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Communications :: File Sharing',
        'Typing :: Typed'
    ],
    keywords='bittorrent bencode',
    python_requires='>=3.6',
    install_requires=[
        # required for typing.Literal
        'typing-extensions; python_version < "3.8"'
    ],
    zip_safe=False
)
