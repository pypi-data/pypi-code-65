from pathlib import Path

from setuptools import find_packages, setup

root = Path(__file__).parent.resolve()

long_description = (root / 'README.md').read_text(encoding='utf-8')
version = (root / 'version.txt').read_text(encoding='utf-8')

setup(
    name='lordcommander',
    description='Run shell commands recursively throughout the predefined directories',
    packages=find_packages(exclude=['test.*', 'test', 'docs.*', 'docs']),
    version=version,
    entry_points={
        'console_scripts': [
            'lc=lordcommander:main',
        ],
    },
    install_requires=[
        'colr >= 0.9',
        'fire >= 0.2',
        'appdirs>=1.4'
    ],
    tests_require=[
        'pytest>=5.4.3',
    ],
    python_requires=">=3.7",
    author='Sowren Sen',
    author_email='sowrensen@gmail.com',
    url='https://github.com/sowrensen/LordCommander',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['shell', 'commands', 'directory', 'projects', 'instances', 'linux', 'sever', 'devops'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Version Control",
        "Topic :: System :: Shells",
        "Topic :: System :: Installation/Setup",
        "Topic :: Terminals"
    ]
)
