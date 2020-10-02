import argparse
import sys, os
import requests


def post_message(token, channel, text, username, icon_emoji):

    url = 'https://slack.com/api/chat.postMessage'
    headers = {'Authorization': 'Bearer ' + token}
    payload = {
        'username': username,
        'channel': channel,
        'text': text,
        'icon_emoji': icon_emoji
    }
    return requests.post(url, data=payload, headers=headers)


def send_file(token, channel, initial_comment, username, filepath):
    if not os.path.exists(filepath):
        print('file not found! %s ' % filepath)
        return 

    url = 'https://slack.com/api/files.upload'
    headers = {'Authorization': 'Bearer ' + token}
    payload = {
        'username': username,
        'channels': channel,
        'initial_comment': initial_comment
    }
    files = {"file": open(filepath, "rb")}
    return requests.post(url, data=payload, headers=headers, files=files)
