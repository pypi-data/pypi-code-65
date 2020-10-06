#! /usr/bin/env python3


import urllib.request
import json
import re


class TwitchAPI():
    __api_headers = {
        'Client-ID': 'm3ggy4wqrvs4sfhv996glushskv1fi',
        'Accept': 'application/vnd.twitchtv.v5+json'}

    def __request(self, url):
        try:
            r = urllib.request.Request(url, headers=self.__api_headers)
            # url checked with regex
            f = urllib.request.urlopen(r)  # nosec
            return json.loads(f.read().decode('utf-8'))
        except Exception as e:
            print("Error using Twitch API: ", e)

    def __raw_data(self, value_list):
        values = ','.join(value_list)
        u = f'https://api.twitch.tv/kraken/users?login={values}'

        # regex to check url
        r = re.compile(
            r'(^https://api.twitch.tv/kraken/users\?login=)'
            r'([a-z0-9_],?)+$')
        match = r.match(u)

        if match:
            url = match.group()
            jsondata = self.__request(url)
            if jsondata['_total'] and jsondata['_total'] > 0:
                return jsondata
            else:
                print(f'No users found with names: {values}')

    def __raw_online(self, value_list):
        values = ','.join(value_list)
        u = f'https://api.twitch.tv/kraken/streams/?channel={values}'

        # regex to check url
        r = re.compile(
            r'(^https://api.twitch.tv/kraken/streams/\?channel=)'
            r'([0-9]+,?)+$')
        match = r.match(u)

        if match:
            url = match.group()
            jsondata = self.__request(url)
            if jsondata and 'streams' in jsondata:
                if jsondata['streams']:
                    return jsondata

    def get_data(self, value_list):
        values = []
        raw_data = self.__raw_data(value_list)
        if raw_data and 'users' in raw_data:
            for user in raw_data['users']:
                values.append(user)
            return values

    def is_online(self, value_list):
        streams = self.__raw_online(value_list)
        if streams and 'streams' in streams:
            return streams['streams']
