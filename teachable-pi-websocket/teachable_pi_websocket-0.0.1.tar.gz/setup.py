from setuptools import setup

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'teachable_pi_websocket',
    packages = ['teachable_pi_websocket'],
    version = '0.0.1',
    license = 'MIT',
    author = 'Lukas Kirner',
    author_email = 'lukas.kirner@gmail.com',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/lukaskirner/teachable-pi-websocket',
    download_url = 'https://github.com/user/reponame/archive/v_01.tar.gz',
    keywords = ['Teachable Machine', 'picamera', 'Raspberry Pi'],
    install_requires=[
        'tornado',
        'picamera',
    ],
    entry_points = {
        'console_scripts': ['teachable-pi-websocket=teachable_pi_websocket.command_line:main'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)