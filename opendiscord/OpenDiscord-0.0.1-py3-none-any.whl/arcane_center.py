'''
arcane_center is an Discord Bot listing site, this is an API wrapper for it.

Example
.. highlight:: python
.. codeblock:: python

    from OpenDiscord import arcane_center

    arcane_center_api = arcane_center.API(bot_id, authorization)

    arcane_center_api.post_server_count(1)
    arcane_center_api.post_shard_count(1)
    ...
'''
import json
import requests


class API:
    '''
    The API wrapper for arcane-center a Discord Bot listing site.
    '''
    def __init__(self, bot_id, authorization):
        '''
        bot_id: The bot id to use with the API.
        authorization: Get this from https://docs.arcane-center.xyz/how-to-get-an-access-token

        Example
        .. highlight:: python
        .. codeblock:: python

            from OpenDiscord import arcane_center

            arcane_center_api = arcane_center.API(bot_id, authorization)
            ...
        '''
        self.bot_id = bot_id
        self.authorization = authorization

        self.url = f"https://arcane-botcenter.xyz/api/{self.bot_id}"

    def post_server_count(self, server_count):
        '''
        server_count: The total servers your bot is in.

        returns: Status code of the request.
        Example
        .. highlight:: python
        .. codeblock:: python

            from OpenDiscord import arcane_center

            arcane_center_api = arcane_center.API(bot_id, authorization)
            arcane_center_api.post_server_count(server_count)
            ...
        '''
        headers = {
            'Authorization': self.authorization,
            'Content-Type': 'application/json'
        }

        payload = {
            'server_count': server_count
        }

        data = json.dumps(payload, sort_keys=True, indent=4, separators=(',', ': '))
        request = requests.post(self.url + "/stats", data=data, headers=headers)
        return request.status_code

    def post_shard_count(self, shard_count):
        '''
        shard_count: The total shards your bot has.
        returns: The status code of the request that has been done

        Example
         .. highlight: python
         .. codeblock:: python

            from OpenDiscord import arcane_center

            arcane_center_api = arcane_center.API(bot_id, authorization)
            arcane_center_api.post_shard_count(shard_count)
            ...
        '''
        headers = {
            'Authorization': self.authorization,
            'Content-Type': 'application/json'
        }

        payload = {
            'shard_count': shard_count
        }

        data = json.dumps(payload, sort_keys=True, indent=4, separators=(',', ': '))
        request = requests.post(self.url + "/stats", data=data, headers=headers)
        return request.status_code
