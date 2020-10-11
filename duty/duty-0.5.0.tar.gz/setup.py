# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['duty']

package_data = \
{'': ['*']}

install_requires = \
['failprint>=0.6.0,<0.7.0']

entry_points = \
{'console_scripts': ['duty = duty.cli:main']}

setup_kwargs = {
    'name': 'duty',
    'version': '0.5.0',
    'description': 'A simple task runner.',
    'long_description': '# Duty\n\n[![ci](https://github.com/pawamoy/duty/workflows/ci/badge.svg)](https://github.com/pawamoy/duty/actions?query=workflow%3Aci)\n[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://pawamoy.github.io/duty/)\n[![pypi version](https://img.shields.io/pypi/v/duty.svg)](https://pypi.org/project/duty/)\n\nA simple task runner.\n\nInspired by [Invoke](https://github.com/pyinvoke/invoke).\n\n![demo](demo.svg)\n\n## Requirements\n\nDuty requires Python 3.6 or above.\n\n<details>\n<summary>To install Python 3.6, I recommend using <a href="https://github.com/pyenv/pyenv"><code>pyenv</code></a>.</summary>\n\n```bash\n# install pyenv\ngit clone https://github.com/pyenv/pyenv ~/.pyenv\n\n# setup pyenv (you should also put these three lines in .bashrc or similar)\nexport PATH="${HOME}/.pyenv/bin:${PATH}"\nexport PYENV_ROOT="${HOME}/.pyenv"\neval "$(pyenv init -)"\n\n# install Python 3.6\npyenv install 3.6.12\n\n# make it available globally\npyenv global system 3.6.12\n```\n</details>\n\n## Installation\n\nWith `pip`:\n```bash\npython3.6 -m pip install duty\n```\n\nWith [`pipx`](https://github.com/pipxproject/pipx):\n```bash\npython3.6 -m pip install --user pipx\n\npipx install --python python3.6 duty\n```\n\n## Quick start\n\nProper documentation pages will soon be available.\n\n### Configuration\n\nCreate a `duties.py` file at the root of your repository.\n\nEach task is declared as a "duty", using the `duty.duty` decorator.\n\n```python\nfrom duty import duty\n\n@duty\ndef docs(ctx):\n    ctx.run("mkdocs build", title="Building documentation")\n```\n\nThe `ctx` argument is the "context" of the duty.\nIt is automatically created and passed to your function.\n\nIt has only one purpose: running command with its `run` method.\nThe `run` method accepts strings, list of strings, or even Python callables.\n\nThe above duty can be rewritten as:\n\n```python\nfrom duty import duty\n\n@duty\ndef docs(ctx):\n    ctx.run(["mkdocs", "build"], title="Building documentation")\n    # avoid the overhead of an extra shell process\n```\n\nOr:\n\n```python\nfrom duty import duty\nfrom mkdocs import build, config\n\n@duty\ndef docs(ctx):\n    ctx.run(build.build, args=[config.load_config()], title="Building documentation")\n    # avoid the overhead of an extra Python process\n```\n\nThe `run` methods accepts various options,\nmostly coming from its underlying dependency:\n[`failprint`](https://github.com/pawamoy/failprint).\n\n**Arguments of the `run` method:**\n\nName | Type | Description | Default\n---- | ---- | ----------- | -------\ncmd | `str`, `list of str`, or Python callable | The command to run. | *required*\nargs | `list` | Arguments to pass to the callable. | `[]`\nkwargs | `dict` | Keyword arguments to pass to the callable. | `{}`\nnumber | `int` | The command number (useful for the `tap` format). | `None`\noutput_type | `str` | The type of output: `stdout`, `stderr`, `combine` or `nocapture` | `combine`\ntitle | `str` | The command title. | *cmd as a shell command or Python statement*\nfmt | `str` | The output format as a Jinja template: `pretty`, `tap` or `custom=...` | `pretty`\npty | `bool` | Whether to run in a PTY. | `False`\nprogress | `bool` | Whether to show progress. | `True`\nnofail | `bool` | Whether to always succeed. | `False`\nquiet | `bool` | Don\'t print the command output, even if it failed. | `False`\nsilent | `bool` | Don\'t print anything. | `False`\n\nExample usage of the `silent` option:\n\n```python\n@duty\ndef clean(ctx):\n    ctx.run("find . -type d -name __pycache__ | xargs rm -rf", silent=True)\n```\n\nNow let\'s say you have more than one command, and you want to silence all of them:\n\n```python\n@duty(silent=True)\ndef clean(ctx):\n    ctx.run("rm -rf .coverage*")\n    ctx.run("rm -rf .mypy_cache")\n    ctx.run("rm -rf .pytest_cache")\n    ctx.run("rm -rf build")\n    ctx.run("rm -rf dist")\n    ctx.run("rm -rf pip-wheel-metadata")\n    ctx.run("rm -rf site")\n    ctx.run("find . -type d -name __pycache__ | xargs rm -rf")\n    ctx.run("find . -name \'*.rej\' -delete")\n```\n\n### Run\n\nTo run a duty, simply use:\n\n```bash\nduty clean\n```\n\nIf you are using [Poetry](https://github.com/python-poetry/poetry):\n\n```bash\npoetry run duty clean\n```\n\nYou can pass multiple duties in one command:\n\n```bash\nduty clean docs\n```\n\nIf one of your duties accept arguments,\nyou can pass them on the command line as well:\n\n```python\n@duty\ndef docs(ctx, serve=False):\n    command = "serve" if serve else "build"\n    ctx.run(f"mkdocs {command}")\n```\n\n```bash\nduty docs serve=1\n```\n\n!!! note\n    Note that arguments are not type-casted:\n    they are always passed as strings to the duties.\n\n## Todo\n\n- Better handling of missing duties arguments.\n  Maybe simply print the error without a traceback:\n  `release() missing 1 required positional argument: \'version\'`\n- Arguments type casting, ideally based on type annotations!',
    'author': 'Timothée Mazzucotelli',
    'author_email': 'pawamoy@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pawamoy/duty',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
