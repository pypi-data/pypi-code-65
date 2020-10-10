# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['falocalrepo_server']

package_data = \
{'': ['*'], 'falocalrepo_server': ['templates/*']}

install_requires = \
['falocalrepo-database>=3.6.1,<3.7.0', 'flask==1.1.2']

entry_points = \
{'console_scripts': ['falocalrepo-server = falocalrepo_server.__main__:main']}

setup_kwargs = {
    'name': 'falocalrepo-server',
    'version': '1.3.2',
    'description': 'Web interface for falocalrepo.',
    'long_description': '# FALocalRepo-Server\n\nWeb interface for [falocalrepo](https://pypi.org/project/falocalrepo/).\n\n## Installation & Requirements\n\nTo install the program it is sufficient to use Python pip and get the package `falocalrepo-server`.\n\n```shell\npython3 -m pip install falocalrepo-server\n```\n\nPython 3.8 or above is needed to run this program, all other dependencies are handled by pip during installation. For information on how to install Python on your computer, refer to the official website [Python.org](https://www.python.org/).\n\nFor the program to run, a properly formatted database created by falocalrepo needs to be present in the same folder.\n\n## Usage\n\n```\nfalocalrepo-server [<host>:<port>]\n```\n\nThe command accepts a single optional argument to manually set host and port. By default the server is run on 0.0.0.0:8080.\n\nOnce the server is running - it will display status messages in the terminal - the web app can be accessed at http://0.0.0.0:8080/, or any manually set host/port combination.\n\n_Note:_ All the following paths are meant as paths from `<host>:<port>`.\n\nThe root folder `/` displays basic information on the database and has links to perform submissions and journal searches.\n\n### User\n\nThe `/user/<username>` path displays basic statistics of a user stored in the database. Clicking on gallery/scraps or journals counters opens submissions and journals by the user respectively.\n\nThe `/submissions/<username>` and `/journals/<username>` paths open submissions and journals by the user respectively.\n\n### Search\n\nThe server search interface allows to search both submissions and journals. Respectively, these can be reached at `/search/submissions` and `/search/journals`. The `/search/` path defaults to submissions search.\n\nThe interface supports the search fields supported by the command line database search commands. To add a field press on the `+` button after selecting one in the dropdown menu. The `-` buttons allow to remove a field from the search.\n\nFields can be added multiple times and will act as OR options.\n\nThe order field allows to sort the search result. By default submissions and journals are sorted by author and ID. For a list of possible sorting fields, see [#Submissions](https://gitlab.com/MatteoCampinoti94/FALocalRepo#submissions) and [#Journals](https://gitlab.com/MatteoCampinoti94/FALocalRepo#journals) in the database section of FALocalRepo readme.\n\nFields are matched using the SQLite [`like`](https://sqlite.org/lang_expr.html#like) expression which allows for limited pattern matching. See [`database` command](https://gitlab.com/MatteoCampinoti94/FALocalRepo#database) for more details.\n\nThe `/submissions/<username>/` and `/journals/<username>/` paths allow to quickly open a search for submissions and journals by `<username>`. `/search/submissions/<username>/` and `/search/journals/<username>/` are also allowed.\n\nResults of the search are displayed 50 per page in a table. Clicking on any row opens the specific item. Clicking on the table headers allows to perform re-sort the search results.\n\n### Submissions & Journals\n\nSubmissions and journals can be accessed respectively at `/submission/<id>` and `/journal/<id>`. All the metadata, content and files that are recorded in the database are displayed in these pages.\n\nSubmission files can be accessed at `/submission/<id>/file`.\n',
    'author': 'Matteo Campinoti',
    'author_email': 'matteo.campinoti94@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/MatteoCampinoti94/falocalrepo-server',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
