'''
This is the blist.xyz API Wrapper.

Example
```py
from OpenDiscord import blist

blist_api = blist.api(bot_id, token) # Token is optional unless you are doing a POST request.

id = blist_api.get_id()
name = blist_api.get_name()

owners = blist_api.get_owners() # Will return a list of all the owner's ids
for owner in owners:
    print(owner)
```
'''
import json
from datetime import datetime

import requests

class API:
    '''
    The actual API Wrapper class
    '''
    def __init__(self, bot_id, authorization=None):
        '''
        bot_id: The bot id this cannot be None.
        authorization: Authorization this can be None
        '''
        self.bot_id = bot_id
        self.authorization = authorization

        self.url = "https://blist.xyz/api"

    def get_id(self):
        '''
        The target bots ID
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        return int(request['id'])

    def get_name(self):
        '''
        Name of the bot
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        return request['name']

    def get_main_owner(self):
        '''
        ID of the bots main owner
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        return int(request['main_owner'])

    def get_owners(self):
        '''
        The bots secondary owners
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        owners_string = request['owners'].split()
        owners_int = []
        for owner in owners_string:
            owners_int.append(int(owner))
        return owners_int

    def get_library(self):
        '''
        The library the bot is coded in
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        return request['library']

    def get_website(self):
        '''
        The bots website
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        return request['website']

    def get_github(self):
        '''
        The bots github repo
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        return request['github']

    def get_short_description(self):
        '''
        The bots short description
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        return request['short_description']

    def get_prefix(self):
        '''
        The bots prefix
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        return request['prefix']

    def get_invite_url(self):
        '''
        The bots invite url
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        return request['invite_url']

    def get_support_server(self):
        '''
        The invite code of the bots support server
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        return request['support_server']

    def get_tags(self):
        '''
        List of bots categories its been tagged with
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        return request['tags']

    def get_monthly_votes(self):
        '''
        Amount of times the bots been voted for during the current month
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        return request['monthly_votes']

    def get_total_votes(self):
        '''
        Amount of times the bots been voted for
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        return request['total_votes']

    def get_certified(self):
        '''
        Whether the bot is certified
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        if request['certified'] == 'false':
            return False
        return True

    def get_vanity_url(self):
        '''
        The bots vanity
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        return request['vanity_url']

    def get_server_count(self):
        '''
        The bots server count
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        return request['server_count']

    def get_shard_count(self):
        '''
        The bots shard count
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        return request['shard_count']

    def get_add_date(self):
        '''
        Returns the add data and time in the following format: Y-M-D H:M:S
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        return datetime.utcfromtimestamp(request['add_date']).strftime('%Y-%m-%d %H:%M:%S')

    def get_invites(self):
        '''
        Amount of times the bot has been invited from the site
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        return request['invites']

    def get_page_views(self):
        '''
        Amount of times the page has been viewed
        '''
        request = requests.get(self.url + f"/bot/{self.bot_id}/stats/").json()
        return request['page_views']

    def post_server_count(self, server_count):
        '''
        server_count: The total servers your bot is in.

        Posts the server count, requires authorization to be set.
        '''
        header = {
            "Authorization": self.authorization
        }

        payload = {
            "server_count": server_count
        }
        data = json.dumps(payload, sort_keys=True, indent=4, separators=(',', ': '))
        request = requests.post(self.url + f"/bot/{self.bot_id}/stats", header=header, data=data)
        return request.status_code

    def post_shard_count(self, shard_count):
        '''
        shard_count: The total shards the bot currently has.

        Posts the shard count, requires Authorization to be set.
        '''
        header = {
            "Authorization": self.authorization
        }

        payload = {
            "shard_count": shard_count
        }
        data = json.dumps(payload, sort_keys=True, indent=4, separators=(',', ': '))
        request = requests.post(self.url + f"/bot/{self.bot_id}/stats", header=header, data=data)
        return request.status_code

    def get_user_id(self, user_id):
        '''
        id: The User ID

        Returns the User ID
        '''
        request = requests.get(self.url + f"/user/{user_id}/").json()
        return int(request['id'])

    def get_user_bio(self, user_id):
        '''
        Gets the user's bio
        '''
        request = requests.get(self.url + f"/user/{user_id}/").json()
        return str(request['bio'])

    def get_user_staff(self, user_id):
        '''
        Returns True if the user is staff False if not
        '''
        request = requests.get(self.url + f"/user/{user_id}/").json()
        if request['staff'] == 'false':
            return False
        return True

    def get_user_joined_at(self, user_id):
        '''
        Returns the date and time when a user joined
        '''
        request = requests.get(self.url + f"/user/{user_id}/").json()
        return datetime.utcfromtimestamp(request['joined_at']).strftime('%Y-%m-%d %H:%M:%S')

    def get_user_reddit(self, user_id):
        '''
        Gets the user's reddit name.
        '''
        request = requests.get(self.url + f"/user/{user_id}/").json()
        return str(request['reddit'])

    def get_user_snapchat(self, user_id):
        '''
        Gets the user's snapchat name.
        '''
        request = requests.get(self.url + f"/user/{user_id}/").json()
        return str(request['snapchat'])

    def get_user_instagram(self, user_id):
        '''
        Gets the user's instagram name
        '''
        request = requests.get(self.url + f"/user/{user_id}/").json()
        return str(request['instagram'])

    def get_user_twitter(self, user_id):
        '''
        Gets the user's twitter name
        '''
        request = requests.get(self.url + f"/user/{user_id}/").json()
        return str(request['twitter'])

    def get_user_github(self, user_id):
        '''
        Returns the github name of the user
        '''
        request = requests.get(self.url + f"/user/{user_id}/").json()
        return str(request['github'])

    def get_user_website(self, user_id):
        '''
        Returns the user's website if it is set
        '''
        request = requests.get(self.url + f"/user/{user_id}/").json()
        return str(request['website'])

    def get_user_bots(self, user_id):
        '''
        Returns the amount of bots the user owns (int)
        '''
        request = requests.get(self.url + f"/user/{user_id}/").json()
        return int(request['bots'])

    def has_voted(self, user_id):
        '''
        This function is not tested because I can't, make sure to avoid using it.
        '''
        headers = {
            "Authorization": self.authorization
        }


        request = requests.get(self.url + f"/bot/{self.bot_id}/votes/", headers=headers).json()
        votes = request['votes']
        if user_id in votes:
            return votes[user_id]
        return None

    def get_widget(self, style: str = None):
        '''
        Returns the widget url for the bot. Style can only normal as of 2020, 4 oct
        '''
        if style is None:
            return self.url + f"/bot/{self.bot_id}/widget/?type=normal"
        return self.url + f"/bot/{self.bot_id}/widget/?type={style}"
