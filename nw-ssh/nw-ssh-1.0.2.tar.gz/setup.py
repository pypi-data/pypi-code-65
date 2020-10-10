# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['nw_ssh']

package_data = \
{'': ['*']}

install_requires = \
['asyncssh>=2.4.2,<3.0.0']

setup_kwargs = {
    'name': 'nw-ssh',
    'version': '1.0.2',
    'description': 'Simple ssh client with asyncssh for network devices',
    'long_description': "# nw-ssh\nSimple ssh client with asyncssh for network devices.\n\n```\nimport asyncio\nfrom nw_ssh import connection\n\nasync def main():\n    async with connection.SSHConnection(\n            host='169.254.0.1',\n            port=22,\n            username='root',\n            password='password',\n            client_keys=[],\n            passphrase=None,\n            known_hosts_file=None,\n            delimiter=r'#',\n            timeout=10) as conn:\n\n        print(conn.login_message)\n\n        output = await conn.send(input='cli', delimiter=r'>')\n        print(output)\n\n        output = await conn.send(input='show interfaces fxp0 | no-more', delimiter=r'>')\n        print(output)\n\n        output = await conn.send(input='configure', delimiter=r'#')\n        print(output)\n\n        output = await conn.send(input='show interfaces', delimiter=r'#')\n        print(output)\n\n        output = await conn.send(input='commit', delimiter=r'#', timeout=10)\n        print(output)\n\nloop = asyncio.get_event_loop()\nloop.run_until_complete(main())\n```\n\n\n# License\nMIT\n\n",
    'author': 'kthrdei',
    'author_email': 'kthrd.tech@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kthrdei/nw-ssh',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
