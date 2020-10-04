'''
Just the same as everything else. Define the class, call a method.
'''
import json
import requests

class API:
    '''
    The API wrapper for bots.ondiscord.xyz
    '''
    def __init__(self, bot_id, authorization):
        '''
        bot_id: The bot id.
        authorization: The API Token.
        '''
        self.bot_id = bot_id
        self.authorization = authorization
        self.url = "https://bots.ondiscord.xyz/bot-api/bots"

    def post_guild_count(self, guild_count):
        '''
        guild_count: The total guilds the bot is currently in.
        returns the status code of the request.
        '''
        headers = {
            "Authorization": self.authorization,
            "Content-Type": "application/json"
        }
        payload = {
            "guildCount": guild_count
        }

        data = json.dumps(payload, sort_keys=True, indent=4, separators=(',', ': '))
        request = requests.post(f"{self.url}/{self.bot_id}/guilds", headers=headers, data=data)
        return request.status_code

    def review_exists(self, user_id):
        '''
        user_id: The user id to check
        returns True if the user posted a review for your bot false if not.
        '''
        headers = {
            "Authorization": self.authorization
        }
        request = requests.get(f"{self.url}/{self.bot_id}/review?owner={user_id}", headers=headers).json()
        if request['exists'] == 'false':
            return False
        return True
