# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pocketsmith_web', 'pocketsmith_web.util']

package_data = \
{'': ['*']}

modules = \
['LICENSE', 'CHANGELOG']
install_requires = \
['aiostream>=0.4.1,<0.5.0',
 'beautifulsoup4>=4.7.1,<5.0.0',
 'httpx>=0.15.5,<0.16.0',
 'lifter>=0.4.1,<0.5.0',
 'pyotp>=2.3.0,<3.0.0',
 'websockets>=8.1,<9.0']

setup_kwargs = {
    'name': 'pocketsmith-web-client',
    'version': '0.1.0',
    'description': 'Pocketsmith web/realtime client, for things the API does not provide',
    'long_description': '# pocketsmith-web-client\n\nA web-based client for Pocketsmith, which adds support for a few things missing from the API:\n\n - Searching transactions\n - Syncing institutions, including those requiring MFA!\n - Real-time events through [Pusher](https://pusher.com/) (just like the web UI)\n\n\n# Installation\n\n```bash\npip install pocketsmith-web-client\n```\n\n\n# Usage\n\n```python\nimport asyncio\nfrom pocketsmith_web import PocketsmithWebClient\n\npwc = PocketsmithWebClient(\n    username=\'hambob\',\n    password=\'Myspace123\',\n    # If 2fa is enabled on the account — NOTE: this is the KEY, not a one-time code!\n    totp_key=\'81r0dq0815u88qi2\',\n)\n\nasync def main():\n    # Check login — NOTE: API methods requiring auth will automatically call this\n    await pwc.login()\n\n    # Search for some transactions and print them out\n    async for transaction in pwc.search_transactions(\'Merchant, inc\'):\n        print(f\'[{transaction["id"]:>8}] {transaction["date"]:%Y-%m-%d} ${transaction["amount"]:.2f}\')\n\n    # Sync some institutions\n    # NOTE: these parameters can be scraped from the Account Summary page, \n    #       in URLs of the format: "/feeds/user_institutions/<uys_id>/refresh?item_ids%5B%5D=<item_id>\n    await pwc.sync_institution(162303, 91821548)\n\nasyncio.run(main())\n```\n\nIf you have an institution requiring MFA info, the Pusher client can be used to provide this info when requested. It\'s up to you to figure out how to acquire the MFA info, though — whether it\'s from user input, a generated TOTP, a text message, email, etc.\n\n```python\nimport asyncio\nimport json\nfrom pocketsmith_web import PocketsmithWebClient, PusherEvent\n\npwc = PocketsmithWebClient(\'hambob\', \'Myspace123\', totp_key=\'81r0dq0815u88qi2\')\n\n\nasync def sync_my_mfa_bank():\n    uys_id = 162303\n    item_id = 91821548\n\n    await pwc.sync_institution(uys_id, item_id)\n\n    async with pwc.pusher() as pusher:\n        # Wait for an MFA event for our bank\n        await pusher.events.expect(\n            PusherEvent.MfaChanged(pwc.pusher_channel),\n            matches_uys_item(uys_id, item_id),\n        )\n\n        # Grab the MFA popup form details\n        mfa_req = await pwc.get_mfa_form_info()\n\n        # Ask the user for the MFA deets, please\n        print(f\'MFA deets required: {mfa_req["label"]}\')\n        token = input(\'Token: \')\n\n        # Now shoot the token back to Pocketsmith\n        await pwc.provide_feed_mfa(uys_id, item_id, token)\n\ndef matches_uys_item(uys_id, item_id):\n    uys_id = str(uys_id)\n    item_id = str(item_id)\n\n    def does_event_match_uys_item(event: PusherEvent):\n        if not isinstance(event.data, dict):\n            return False\n\n        event_uys_id = event.data.get(\'user_yodlee_site_id\')\n\n        event_items = event.data.get(\'new_mfa_items\', ())\n        if isinstance(event_items, str):\n            try:\n                event_items = json.loads(event_items)\n            except (TypeError, ValueError):\n                pass\n\n        return uys_id == event_uys_id and item_id in event_items\n\n    return does_event_match_uys_item\n\n\nasyncio.run(sync_my_mfa_bank())\n```\n',
    'author': 'Zach "theY4Kman" Kanzler',
    'author_email': 'they4kman@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/theY4Kman/python-pocketsmith-api',
    'packages': packages,
    'package_data': package_data,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1',
}


setup(**setup_kwargs)
