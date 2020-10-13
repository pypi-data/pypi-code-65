from json import loads, dumps
from logging import getLogger
from requests import request
from django.conf import settings

LOGGER = getLogger('django')
CONSUL_CONFIGS = settings.CONSUL_CONFIGS
CONSUL_SECRETS = settings.CONSUL_SECRETS


def record(func):
    """ 保存发送通知的记录 """
    def _inner(*args, **kwargs):
        # send_to = kwargs['send_to']
        # message = kwargs['message']
        # LOGGER.info('Notification, send to "%s", message is %s', send_to, message)
        _result = func(*args, **kwargs)
        # TODO: 保存发送通知的记录
        return _result
    return _inner


class Notification(object):
    """ Notifications subclass must redefine the send method. """

    def send(self, send_to=None, message=None, **kwargs):
        """ 发送消息的具体动作, 子类必须重写 """
        raise NotImplementedError('Notifications subclass must redefine the send method.')

    @record
    def info(self, send_to=None, message=None, **kwargs):
        message = '[INFO] ' + message
        self.send(send_to, message, **kwargs)

    @record
    def warning(self, send_to=None, message=None, **kwargs):
        message = '[WARN] ' + message
        self.send(send_to, message, **kwargs)

    @record
    def error(self, send_to=None, message=None, **kwargs):
        message = '[ERROR] ' + message
        self.send(send_to, message, **kwargs)


class EnterpriseWeXinAgent(Notification):
    def __init__(self, corpid, agentid, corpsecret):
        self.agentid = agentid
        self.get_token_baseurl = CONSUL_CONFIGS.get(
            'WX_TOKEN_BASEURL', 'https://qyapi.weixin.qq.com/cgi-bin/gettoken')
        self.send_message_baseurl = CONSUL_CONFIGS.get(
            'WX_MESSAGE_BASEURL', "https://qyapi.weixin.qq.com/cgi-bin/message/send")
        self._token = self._access_token(corpid, corpsecret)

    def _access_token(self, corpid, corpsecret):
        """ Get the access token from enterprise wexin, return a token str """
        url = f"{self.get_token_baseurl}?corpid={corpid}&corpsecret={corpsecret}"
        try:
            response = request('GET', url=url)
            if response.status_code == 200:
                context = loads(response.content)
                if context['errcode'] == 0:
                    LOGGER.info('EnterpriseWeXinAgent, access token has been received')
                    return context['access_token']
                LOGGER.error('EnterpriseWeXinAgent, Get the access token error, %s', context)
            else:
                LOGGER.error(
                    'EnterpriseWeXinAgent, Get access token error, '
                    'http response status code is %s', response.status_code)
                return None
        except Exception as error:
            LOGGER.exception('EnterpriseWeXinAgent, Get the access token error, %s', error)
            return None

    def send(self, send_to=None, message=None, **kwargs):
        try:
            url = f'{self.send_message_baseurl}?access_token={self._token}'
            data = {
                "touser" : send_to,
                "msgtype" : "text",
                "agentid" : self.agentid,
                "text" : {"content" : message},
                "safe":0,
                "enable_id_trans": 0,
                "enable_duplicate_check": 0,
                "duplicate_check_interval": 1800
            }
            kwargs.setdefault('data', data)
            response = request('POST', url=url, data=dumps(kwargs['data']))
            if response.status_code == 200:
                context = loads(response.content)
                if context['errcode'] == 0:
                    LOGGER.info('EnterpriseWeXinAgent, send the notification is successful')
                else:
                    LOGGER.error('EnterpriseWeXinAgent, send the notification error, %s', context)
            else:
                LOGGER.error(
                    'EnterpriseWeXinAgent, Unable to send notification, '
                    'status code is %s', response.status_code)
        except Exception as error:
            LOGGER.exception(error)



class EnterpriseWeXinRobot(Notification):
    def send(self, send_to=None, message=None, **kwargs):
        pass


class InfraAlert(Notification):
    def send(self, send_to=None, message=None, **kwargs):
        pass
