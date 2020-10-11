#! /usr/bin/env python3


import os
import re
import webbrowser
import subprocess
import datetime
from pathlib import Path

from . import twitch
from . import fileoperator


class StreamerItems():

    _keys = {
        'title': 'status',
        'dispName': 'display_name',
        'game': 'game',
        'id_': '_id',
        'name': 'name',
        'logo': 'logo',
        'screenshot': 'video_banner',
        'url': 'url',
        'started': 'created_at',
        'timeStreamed': 'streamed'}

    __pretty = {
        'title': 'Title',
        'dispName': 'Display Name',
        'game': 'Game',
        'id_': 'ID',
        'name': 'Name',
        'logo': 'Logo URL',
        'screenshot': 'Screenshot URL',
        'url': 'Stream URL',
        'started': 'Started At',
        'timeStreamed': 'Time'}

    def getKeys(self, pretty=False):
        if not pretty:
            return self._keys.keys()
        else:
            return self.__pretty


class Streamer(StreamerItems):
    """General Streamer parent class."""

    def __init__(self, data):
        """Initialize data."""

        self.__data = data

    def data(self):
        """Return all filtered data."""

        return self.__data

    def name(self):
        """Return name."""

        return self.__data[self._keys['name']]

    def dispName(self):
        """Return display name."""

        return self.__data[self._keys['dispName']]

    def getValue(self, key):
        """Give key and matching value is returned."""

        return self.__data[self._keys[key]]


class StreamerDB(Streamer):
    """Streamer class for local database."""

    def __init__(self, data):
        """Initializes StreamerDB and Streamer."""

        super(StreamerDB, self).__init__(data)
        self.__data = data


class StreamerOnline(Streamer):
    """Streamer class for online streamers."""

    __streaming = 'channel'

    def __init__(self, data):
        """Initializez StreamerOnline and Streamer."""

        self.__rawData = data
        self.__data = data[self.__streaming]
        super(StreamerOnline, self).__init__(self.__data)
        self.streamed()

    def streamed(self):
        """Counts and returns how long stream has been online."""

        stamp = self.__rawData[self._keys['started']]
        time_stamp = datetime.datetime.strptime(stamp, '%Y-%m-%dT%H:%M:%SZ')
        now = datetime.datetime.utcnow()
        delta = now - time_stamp
        time = str(datetime.timedelta(seconds=delta.seconds))
        self.__data['streamed'] = time

    def game(self):
        """Returns game being played."""

        return self.__data[self._keys['game']]

    def url(self):
        """Returns streaming url."""

        return self.__data[self._keys['url']]

    def started(self):
        """Returns when stream started at."""

        return self.__data[self._keys['started']]

    def allData(self):
        """Returns all filtered data in iterable manner."""

        for key in self._keys.values():
            yield self.__data[key]

    def rawData(self):
        """Return raw unedited data."""

        return self.__rawData


class Streamers():
    """Class for governing Streamer local and online data."""

    __bases = {
        'posix': '~/.config/streamchecker',
        'nt': '~/Documents/streamchecker'}
    __base = __bases[os.name]
    _files = {
        'streamersDB': 'streamchecker.json',
        'follows': 'follows.csv'}

    def __init__(self):
        """Initializes Streamers class.

        Uses TwitchAPI() and FileOperator()."""

        self.__twitchApi = twitch.TwitchAPI()
        self._fileObjs = self.__fileObjDict()
        self.loadFollowsDB()
        self.updateFollowsDB()

    def __fileObjDict(self):
        """Creates a directory from file objects used in Streamers()."""

        files = {}
        for f in self._files:
            path = Path(self.__base) / Path(self._files[f])
            files[f] = fileoperator.FileOperator(path)
        return files

    def __streamersValue(self, key):
        """Returns value from local Streamers that matches key."""

        valuelist = []
        for streamer in self.__streamers:
            valuelist.append(streamer.getValue(key))
        return valuelist

    def getKeys(self, pretty=False):
        items = StreamerItems().getKeys(pretty)
        return items

    def loadFollowsDB(self):
        """Loads follows file content into Streamers()."""

        json_data = self._fileObjs['streamersDB'].loadFile()
        streamers = []
        if json_data:
            for streamer in json_data:
                streamers.append(StreamerDB(streamer))
        self.__streamers = streamers

    def updateFollowsDB(self):
        """Updates streamers database if changes in follows file."""

        follows = self._fileObjs['follows'].loadFile(singleLayer=True)
        names = self.__streamersValue('name')
        follows_set = set(follows)
        names_set = set(names)
        if not names_set == follows_set:
            data = False
            if follows:
                data = self.__twitchApi.get_data(follows)
            self._fileObjs['streamersDB'].saveFile(data)
            self.loadFollowsDB()

    def getStreaming(self):
        """Returns online streamer objects."""

        ids = self.__streamersValue('id_')
        if ids:
            online = self.__twitchApi.is_online(ids)
        else:
            online = ''
        streams = []
        if online:
            for onlineStream in online:
                streams.append(StreamerOnline(onlineStream))
        return streams

    def getDb(self):
        """Returns streams from database."""

        return self.__streamers

    def baseFolder(self):
        """Returns base folder used in Streamers()."""

        return self.__base

    def files(self):
        """Returns fileobjects used in Streamers()."""

        return self._fileObjs


class StreamPlay(Streamers):

    def __init__(self, config=False):
        """Initializes StreamPlay and Streamers.

        Adds optional configuration json dictionary file.
        - player
        - player_set
        """

        super(StreamPlay, self).__init__()
        if config:
            self._files['config'] = config
            path = Path(self.baseFolder()) / Path(self._files['config'])
            self._fileObjs['config'] = fileoperator.FileOperator(path)

    def __checkConfigs(self):
        """Checks if configs are found."""

        if 'config' in self._fileObjs:
            configs = self._fileObjs['config'].loadFile() or {}
        else:
            configs = {}
        return configs

    def __run(self, rules, url):
        """Runs the given url."""

        if all(rules[1:]):
            command = rules[-1]
            command.append(url)
        else:
            webbrowser.open(url)
            return

        pid = subprocess.Popen(command, close_fds=True)
        return pid

    def chat(self, stream, default=False, pid=False):
        """Starts chat from the given stream object.

        Input stream object.

        Tries to read player from configuration file. If none found
        starts with default webbrowser. You can force default webbrowser
        usage by having 'chat_set' = False in configuration file or by
        setting default=True when calling the method.

        Link from streamer object is added to the end of the chat
        command.

        Returns pid value if given pid=True as kwarg.
        """

        # regex url before accepting it as value
        r = re.compile(
            r'^(https?://)'
            r'(www\.|m\.)'
            r'(twitch\.tv/)'
            r'([a-zA-Z0-9_]*)$')
        if r.match(stream.url()):
            u = r.match(stream.url()).groups()
            url = ''.join(u[:3]) + 'popout/' + u[3] + '/chat'
        else:
            raise ValueError('Not a valid link')

        configs = self.__checkConfigs()

        rules = [
            pid is True,
            default is False,
            configs.get('chat_set') is True,
            configs.get('chat')]

        pid = self.__run(rules, url)
        if rules[0]:
            return pid

    def play(self, stream, default=False, pid=False):
        """Starts playing given stream object.

        Input stream object.

        Tries to read player from configuration file. If none found
        starts with default webbrowser. You can force default webbrowser
        usage by having 'player_set' = False in configuration file or by
        setting default=True when calling the method.

        Link from streamer object is added to the end of the player
        command.

        Returns pid value if given pid=True as kwarg.
        """

        # regex url before accepting it as value
        r = re.compile(
            r'^(https?://)'
            r'(www\.|m\.)'
            r'(twitch\.tv/)'
            r'([a-zA-Z0-9_]*)$')
        if r.match(stream.url()):
            url = r.match(stream.url()).group()
        else:
            raise ValueError('Not a valid link')

        configs = self.__checkConfigs()

        rules = [
            pid is True,
            default is False,
            configs.get('player_set') is True,
            configs.get('player')]

        pid = self.__run(rules, url)
        if rules[0]:
            return pid


def main():
    """Testing function."""

    pass


if __name__ == '__main__':
    main()
