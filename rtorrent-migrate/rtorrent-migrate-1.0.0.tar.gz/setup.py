import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='rtorrent-migrate',
    version='1.0.0',
    author='Adralioh',
    description='rTorrent migration utility',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/adralioh/rtorrent-migrate',
    project_urls={
        'Documentation': 'https://adralioh.gitlab.io/rtorrent-migrate'
    },
    packages=setuptools.find_packages(exclude=['tests']),
    package_data={
        '': ['py.typed']
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'Topic :: Communications :: File Sharing',
        'Topic :: Utilities',
        'Typing :: Typed'
    ],
    keywords='bittorrent rtorrent',
    python_requires='>=3.6',
    install_requires=[
        'benparse'
    ],
    entry_points={
        'console_scripts': [
            'rtorrent-migrate = rtorrent_migrate.migrator:_main'
        ]
    },
    zip_safe=False
)
