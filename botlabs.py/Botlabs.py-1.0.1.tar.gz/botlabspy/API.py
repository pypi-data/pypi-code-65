import requests


class API:
    token = None
    bot_id = None
    url = None

    def __init__(self, bot_id: int, token: str = None):
        """
        :param bot_id: The Bot ID of the bot.
        :param token: The API token. You can get this token from https://bots.discordlabs.org/bot/{bot_id}/manage, This can be None
        """
        self.bot_id = bot_id
        self.TOKEN = token
        self.url = f'https://bots.discordlabs.org/v2/bot{self.bot_id}'

    def _bot_info(self):
        """
        :return: Returns the json file from the API.
        """
        r = requests.get(self.url + str(self.bot_id))
        data = r.json()
        return data


    def _error(data):
        """
        :param data: A json file.
        :return: True if there is an error False if not.
        """
        if data['error'] is 'true':
            return True
        else:
            return False

    def _error_message(self, data):
        if self._error(data):
            return data['message']
        else:
            raise TypeError('Requested error message when there where no errors.')

    def _get_key(self, data, key):
        if self._error(data):
            print(self._error_message(data))
        else:
            return data[key]

    # Get requests
    def get_name(self):
        """
        :return: The Bot's name.
        """
        data = self._bot_info()
        return self._get_key(data, 'name')

    def get_avatar(self):
        """
        :return: The Bot's avatar URL.
        """
        data = self._bot_info()
        return self._get_key(data, 'avatar')

    def get_short_description(self):
        """
        :return: The short description of the Bot.
        """
        data = self._bot_info()
        return self._get_key(data, 'sdescription')

    def get_long_description(self):
        """
        :return: The long description of the bot.
        """
        data = self._bot_info()
        return self._get_key(data, 'ldescription')

    def get_votes(self):
        """
        :return: The amount of votes a bot has
        """
        data = self._bot_info()
        return self._get_key(data, 'votes')

    def get_server_count(self):
        """
        :return: The amount of servers the bot is in. Must be set using `API.set_server_count`
        """
        data = self._bot_info()
        return self._get_key(data, 'server_count')

    def get_shard_count(self):
        """
        :return: The amount of shards the bot has. Must be set using `API.set_shard_count`
        """
        data = self._bot_info()
        return self._get_key(data, 'shard_count')

    # Post requests
    def set_server_count(self, server_count: str):
        """
        :param server_count: The total server your bot is in.
        :return: A response, use .status_code to see the status code that the POST request returned. Read more @ https://requests.readthedocs.io/en/master/user/quickstart/#response-content
        """
        if self.token is None:
            raise AttributeError('Missing bot token.')
        data = {
            'token': self.token,
            'server_count': server_count
        }
        r = requests.post(self.url + '/stats', data=data)
        return r

    def set_shard_count(self, shard_count: str):
        """
        :param shard_count: The total shards your bot has.
        :return: A response, use .status_code to see the status code that the POST request returned. Read more @ https://requests.readthedocs.io/en/master/user/quickstart/#response-content
        """
        if self.token is None:
            raise AttributeError('Missing bot token.')
        data = {
            'token': self.token,
            'shard_count': shard_count
        }
        r = requests.post(self.url + '/stats', data=data)
        return r
