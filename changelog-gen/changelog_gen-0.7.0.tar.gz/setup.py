# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['changelog_gen', 'changelog_gen.cli']

package_data = \
{'': ['*']}

install_requires = \
['bump2version>=0.5.11,<0.6.0', 'click>=7.0,<8.0']

entry_points = \
{'console_scripts': ['changelog-gen = changelog_gen.cli.command:gen',
                     'changelog-init = changelog_gen.cli.command:init']}

setup_kwargs = {
    'name': 'changelog-gen',
    'version': '0.7.0',
    'description': 'Changelog generation tool',
    'long_description': "# Changelog Generator - v0.7.0\n[![image](https://img.shields.io/pypi/v/changelog_gen.svg)](https://pypi.org/project/changelog_gen/)\n[![image](https://img.shields.io/pypi/l/changelog_gen.svg)](https://pypi.org/project/changelog_gen/)\n[![image](https://img.shields.io/pypi/pyversions/changelog_gen.svg)](https://pypi.org/project/changelog_gen/)\n![style](https://github.com/EdgyEdgemond/changelog-gen/workflows/style/badge.svg)\n![tests](https://github.com/EdgyEdgemond/changelog-gen/workflows/tests/badge.svg)\n[![codecov](https://codecov.io/gh/EdgyEdgemond/changelog-gen/branch/master/graph/badge.svg)](https://codecov.io/gh/EdgyEdgemond/changelog-gen)\n\n`changelog-gen` is a CHANGELOG generator intended to be used in conjunction\nwith [bumpversion](https://github.com/c4urself/bump2version) to generate\nchangelogs and create release tags.\n\n## Installation\n\n```bash\npip install changelog-gen\n```\n\nor clone this repo and install with poetry, currently depends on poetry < 1.0.0\ndue to other personal projects being stuck.\n\n```bash\npoetry install\n```\n\n## Usage\n\n`changelog-gen` currently only supports reading changes from a `release_notes` folder.\n\nFiles in the folder should use the format `{issue_number}.{type}`.\n\nBy default supported types are currently `fix` and `feat`. Additional types can be configured\nto map to these initial types.\n\nThe contents of each file is used to populate the changelog file. If the type\nends with a `!` it denotes a breaking change has been made, this will lead to a\nmajor release being suggested.\n\n```bash\n$ ls release_notes\n  4.fix  7.fix\n\n$ changelog-gen\n\n## v0.2.1\n\n### Bug fixes\n\n- Raise errors from internal classes, don't use click.echo() [#4]\n- Update changelog line format to include issue number at the end. [#7]\n\nWrite CHANGELOG for suggested version 0.2.1 [y/N]: y\n```\n\n## Configuration\n\nOf the command line arguments, most of them can be configured in `setup.cfg` to remove\nthe need to pass them in every time.\n\nExample `setup.cfg`:\n\n```ini\n[changelog_gen]\ncommit = true\nrelease = true\nallow_dirty = false\n```\n\n### Configuration file -- Global configuration\n\nGeneral configuration is grouped in a `[changelog_gen]` section.\n\n#### `commit = (True | False)`\n  _**[optional]**_<br />\n  **default**: False\n\n  Commit changes to the changelog after writing.\n\n  Also available as `--commit` (e.g. `changelog-gen --commit`)\n\n#### `release = (True | False)`\n  _**[optional]**_<br />\n  **default**: False\n\n  Use bumpversion to tag the release\n\n  Also available as `--release` (e.g. `changelog-gen --release`)\n\n#### `allow_dirty = (True | False)`\n  _**[optional]**_<br />\n  **default**: False\n\n  Don't abort if the current branch contains uncommited changes\n\n  Also available as `--allow-dirty` (e.g. `changelog-gen --allow-dirty`)\n\n#### `issue_link =`\n  _**[optional]**_<br />\n  **default**: None\n\n  Create links in the CHANGELOG to the originating issue. A url that contains an\n  `{issue_ref}` for formatting.\n\n  Example:\n\n```ini\n[changelog_gen]\nissue_link = http://github.com/EdgyEdgemond/changelog-gen/issues/{issue_ref}\n```\n\n#### `allowed_branches =`\n  _**[optional]**_<br />\n  **default**: None\n\n  Prevent changelog being generated if the current branch is not in the supplied list. By\n  default all branches are allowed.\n\n  Example:\n\n```ini\n[changelog_gen]\nallowed_branches = \n  master\n  develop\n```\n\n#### `sections =`\n  _**[optional]**_<br />\n  **default**: None\n\n  Define custom headers or new sections/headers, new sections will require a matching\n  section_mapping configuration.\n\n  Example:\n\n```ini\n[changelog_gen]\nsections = \n  feat=New Features\n  change=Changes\n  remove=Removals\n  fix=Bugfixes\n```\n\n#### `section_mapping =`\n  _**[optional]**_<br />\n  **default**: None\n\n  Configure additional supported release_note extensions to supported changelog\n  sections.\n\n  Example:\n\n```ini\n[changelog_gen]\nsection_mapping = \n  test=fix\n  bugfix=fix\n  docs=fix\n  new=feat\n```\n",
    'author': 'Daniel Edgecombe',
    'author_email': 'edgy.edgemond@gmail.com',
    'url': 'https://github.com/EdgyEdgemond/changelog-gen/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
