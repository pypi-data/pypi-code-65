import requests
import json
from bark_client.utils import logger


class SoundType(object):
    ALARM = 'alarm'
    ANTICIPATE = 'anticipate'
    BELL = 'bell'
    BIRDSONG = 'birdsong'
    BLOOM = 'bloom'
    CALYPSO = 'calypso'
    CHIME = 'chime'
    CHOO = 'choo'
    DESCENT = 'descent'
    ELECTRONIC = 'electronic'
    FANFARE = 'fanfare'
    GLASS = 'glass'
    GOTOSLEEP = 'gotosleep'
    HEALTHNOTIFICATION = 'healthnotification'
    HORN = 'horn'
    LADDER = 'ladder'
    MAILSEND = 'mailsend'
    MINUET = 'minuet'
    MULTIWAYINVITATION = 'multiwayinvitation'
    NEWMAIL = 'newmail'
    NEWSFLASH = 'newsflash'
    NOIR = 'noir'
    PAYMENTSUCCESS = 'paymentsuccess'
    SHAKE = 'shake'
    SHERWOODFOREST = 'sherwoodforest'
    SPELL = 'spell'
    SUSPENSE = 'suspense'
    TELEGRAPH = 'telegraph'
    TIPTOES = 'tiptoes'
    TYPEWRITERS = 'typewriters'
    UPDATE = 'update'


class BarkClient(object):

    def __init__(self, domain, key_list):
        self.domain = domain
        self.key_list = key_list

    def push(self, content, title=None, url=None,
             receivers=None, sound=None, automatically_copy=False):
        failing_receiver = []
        for key in (receivers or self.key_list):
            request_url = 'https://{domain}/{key}'.format(domain=self.domain, key=key)
            if title:
                request_url += '/{title}'.format(title=title)
            request_url += '/{}'.format(content)

            resp = requests.get(request_url, params={
                "automatically_copy": automatically_copy,
                "url": url,
                "sound": sound
            })

            data = json.loads(resp.text)
            if not (resp.status_code == 200 and data['code'] == 200):
                logger.error("Fail to push to [{}], error message = {}".format(key, data['message']))
                failing_receiver.append(key)

        logger.info("Number of failed pushes: {}".format(len(failing_receiver)))
        return failing_receiver
