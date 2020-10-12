import anybadge
import bs4
import json
import logging
import re
import requests
import os
from pkg_resources import resource_string
from .config import loadControl, loadVersionCheck

log = logging.getLogger()


def latestVersion():
    """ Extract latest version defined by version-check.json

    Returns
    -------
    version: string
        version extracted from web page
    """
    config = loadVersionCheck()

    if 'external_check' not in config:
        config['external_check'] = True

    if not config['external_check']:
        control = loadControl()
        return control['version']

    content = requests.get(config['url_version']).text.strip()

    if config['html'] is True:
        soup = bs4.BeautifulSoup(content, 'html.parser')
        if 'index' in config:
            index = config['index']
        else:
            index = 0

        latest_version = soup.select(config['selector'])[index].contents[0].strip()

        # log.debug('index = {}'.format(index))
        # selected = soup.select(config['selector'])
        # log.debug('selected = {}'.format(selected))
        # log.debug('selected[{}] = {}'.format(index, selected[index]))
        # log.debug('selected[{}].contents[0] = {}'.format(index, selected[index].contents[0]))
        # latest_version = selected[index].contents[0].strip()
    else:
        latest_version = content

    if 'cleaners' in config and len(config['cleaners']) > 0:
        for cleaner in config['cleaners']:
            latest_version = re.sub(cleaner['pattern'], cleaner['rewrite'], latest_version, flags=re.DOTALL).strip()

    return latest_version.replace('\n', ' ').replace('\r', '')


def versionChecker(chat=False, badge=False):
    """ Compare latest version defined by version-check.json, versus WAPT/control one

    Parameters
    ----------
    chat: bool
        send results to chat
    badge: bool
        generate upstream badge

    Returns
    -------
    results: bool
        version mismatch
    """
    control = loadControl()
    log.info('Current {} version: {}'.format(control['name'], control['version']))

    latest_version = latestVersion()
    log.info('Latest {} version: {}'.format(control['name'], latest_version))

    if control['version'] != latest_version:
        log.info('New version available, please upgrade package')

        if chat:
            log.debug('Sending message to Chat webhook ...')
            if 'CHAT_WEBHOOK_URL' in os.environ:
                payload = resource_string('wapttools.data', 'chat_message.json')
                payload = payload.replace('{package}', control['name'])
                payload = payload.replace('{old_version}', control['version'])
                payload = payload.replace('{new_version}', latest_version)
                payload = payload.replace('{homepage}', control['homepage'])

                # Compact JSON string
                payload = json.dumps(json.loads(payload), separators=(',', ':'))

                requests.session().post(
                    os.environ['CHAT_WEBHOOK_URL'],
                    data=payload,
                    headers={'Content-Type': 'application/json; charset=UTF-8'}
                )
            else:
                log.warning('CHAT_WEBHOOK_URL environment variable not defined, unable to send chat message')
            log.debug('... done.')

        if badge:
            log.debug('generating badge ...')
            badge = anybadge.Badge(label='upstream', value='new', default_color='red')
            badge.write_badge('upstream.svg')

        return True

    if badge:
        log.debug('generating badge ...')
        badge = anybadge.Badge(label='upstream', value='ok', default_color='green')
        badge.write_badge('upstream.svg')

    return False
