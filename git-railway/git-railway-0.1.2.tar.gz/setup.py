# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['git_railway', 'git_railway.view']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.8,<4.0.0',
 'colour>=0.1.5,<0.2.0',
 'dataclasses',
 'svgwrite>=1.4,<2.0']

entry_points = \
{'console_scripts': ['git-railway = git_railway.__main__:main']}

setup_kwargs = {
    'name': 'git-railway',
    'version': '0.1.2',
    'description': 'Visualise local git branches as neat interactive HTML pages',
    'long_description': '<h1 align="center">Git Railway</h1>\n\n<h3 align="center">Visualise local git branches as neat interactive HTML pages</h3>\n\n<p align="center">\n  <img src="https://upload.wikimedia.org/wikipedia/commons/3/3a/Tux_Mono.svg"\n       height="24px" />\n  &nbsp;&nbsp;&nbsp;&nbsp;\n  <img src="https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg"\n       height="24px" />\n  &nbsp;&nbsp;&nbsp;&nbsp;\n  <img src="https://upload.wikimedia.org/wikipedia/commons/2/2b/Windows_logo_2012-Black.svg"\n       height="24px" />\n</p>\n\n<p align="center">\n  <!-- <a href="https://github.com/P403n1x87/git-railway/actions?workflow=Tests">\n    <img src="https://github.com/P403n1x87/git-railway/workflows/Tests/badge.svg"\n         alt="GitHub Actions: Tests">\n  </a> -->\n  <a href="https://travis-ci.com/P403n1x87/git-railway">\n    <img src="https://travis-ci.com/P403n1x87/git-railway.svg?token=fzW2yzQyjwys4tWf9anS"\n         alt="Travis CI">\n  </a>\n  <!-- <a href="https://codecov.io/gh/P403n1x87/git-railway">\n    <img src="https://codecov.io/gh/P403n1x87/git-railway/branch/master/graph/badge.svg"\n         alt="Codecov">\n  </a> -->\n  <a href="https://pypi.org/project/git-railway/">\n    <img src="https://img.shields.io/pypi/v/git-railway.svg"\n         alt="PyPI">\n  </a>\n  <a href="https://github.com/P403n1x87/git-railway/blob/master/LICENSE.md">\n    <img src="https://img.shields.io/badge/license-GPLv3-ff69b4.svg"\n         alt="LICENSE">\n  </a>\n</p>\n\n<p align="center">\n  <!-- <a href="#synopsis"><b>Synopsis</b></a>&nbsp;&bull; -->\n  <a href="#installation"><b>Installation</b></a>&nbsp;&bull;\n  <a href="#usage"><b>Usage</b></a>\n\t<!-- &nbsp;&bull; -->\n  <!-- <a href="#compatibility"><b>Compatibility</b></a>&nbsp;&bull;\n  <a href="#contribute"><b>Contribute</b></a> -->\n</p>\n\n<p align="center">\n\t<img alt="Git Railway Example"\n\t     src="art/sample.png" />\n</p>\n\n# Installation\n\nInstallation from the repository requires Poetry\n\n~~~\npip install poetry git+https://github.com/p403n1x87/git-railway\n~~~\n\nSoon available from PyPI!\n\n\n# Usage\n\nNavigate to a git repository and run\n\n~~~ shell\ngit-railway\n~~~\n\nYour railway graph will be generated in `railway.html`. Use the `-o` or\n`--output` option to override the default location, e.g.\n\n~~~ shell\ngit-railway --output /tmp/mytemprailwaygraph.html\n~~~\n\nIf the remote repository is hosted on GitHub, you can have issue and PR\nreferences replaced with actual links if you pass the GitHub slug using the\n`--gh` option, e.g.\n\n~~~ shell\ngit-railway --gh p403n1x87/git-railway\n~~~\n\n\n# A word on branches\n\nAs you probably know already, a branch in git is a mere reference (or label)\nthat moves with every new commit. As such, it\'s hard if not impossible to\nreconstruct the *actual* branch from the information available from within a git\nrepository. This tools works by looking at the current local refs and collecting\nall the commits that can be reached from them. The "branches" are the\nreconstructed "best effort" by looking at the reflog to determine on which\ncommit a certain ref has been on. Sometimes this information is missing. For\nexample, when one does a merge by fast-forwarding, all the intermediate commits\nare not marked with the ref of the target branch. Should they be part of the\nbranch or not? Whenever you see a piece of gray rail in the graph, that\'s where\nthe ref information is missing.\n',
    'author': 'Gabriele N. Tornetta',
    'author_email': 'phoenix1987@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/P403n1x87/git-railway',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
