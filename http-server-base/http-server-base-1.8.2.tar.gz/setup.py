import os
import re
from glob import iglob

from setuptools import setup

requirements = [ ]
with open('requirements.txt') as f:
    # noinspection PyRedeclaration
    requirements = f.read().splitlines()

version = ''
with open('src/http_server_base/__init__.py') as f:
    # noinspection PyRedeclaration
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if (not version):
    raise RuntimeError("Package version is not set")

if (version.endswith(('a', 'b', 'rc'))):
    # append version identifier based on commit count
    try:
        import subprocess
        p = subprocess.Popen(['git', 'rev-list', '--count', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += out.decode('utf-8').strip()
        p = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += '+g' + out.decode('utf-8').strip()
    except Exception:
        pass

readme = ''
with open('README.md') as f:
    # noinspection PyRedeclaration
    readme = f.read()

extras_require = { }
for r in iglob('requirements/requirements-*.txt'):
    with open(r) as f:
        reqs = [ l.strip() for l in f ]
        feature_name = re.match(r'requirements-(.*)\.txt', os.path.basename(r)).group(1).title()
        extras_require[feature_name] = reqs
extras_require.setdefault('all', sum(extras_require.values(), list()))

setup \
(
    name = 'http-server-base',
    url = 'https://gitlab.com/Hares-Lab/http-server-base',
    version = version,
    packages =
    [
        'http_server_base',
        'http_server_base.model',
        'http_server_base.tools',
        'http_server_base.restapi',
    ],
    setup_requires = [ 'wheel' ],
    package_dir = { '': 'src' },
    license = "MIT Licence",
    description = "Library for simple HTTP server & REST HTTP server base based on Tornado. Includes: Logging requests and responses with Request Id; Configuration loading; Methods for requests proxying",
    long_description = readme,
    long_description_content_type = 'text/markdown',
    include_package_data = True,
    install_requires = requirements,
    extras_require = extras_require,
    python_requires = '>=3.6.0',
    keywords = [ 'http', 'tornado', 'server', 'http-server', 'restapi', 'rest' ],
    classifiers =
    [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: Proxy Servers',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
    ]
)
