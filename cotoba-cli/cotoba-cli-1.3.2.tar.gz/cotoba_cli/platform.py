import base64
import boto3
import http.client
import json
import logging
import pytz
import re

import click
import botocore

from datetime import datetime
from pytz import timezone

from botocore import exceptions as boto_exceptions

from cotoba_cli import config
from cotoba_cli import cognito
from cotoba_cli.util import api_session, build_url


logger = logging.getLogger(__name__)
aws_config = botocore.config.Config(signature_version=botocore.UNSIGNED)
client = boto3.client('cognito-idp',
                      region_name=cognito.USER_POOL_REGION,
                      config=aws_config)


BOT_API_PATH = 'bots/'


class PlatformResponse:
    def __init__(self,
                 response_body_json,
                 http_status_code,
                 message_text,
                 request_body=None,
                 response_headers=None):
        self.__response_body_json = response_body_json
        self.__http_status_code = http_status_code
        self.__message_text = message_text
        self.__response_headers = response_headers
        self.__request_body = request_body

    def get_response_body(self):
        return json.loads(self.__response_body_json)

    @property
    def message(self):
        return self.__message_text

    @property
    def http_status_code(self):
        return self.__http_status_code

    @message.setter
    def message(self, message):
        self.__message_text = message

    def print_message(self, output_headers):
        if not (self.__message_text or output_headers):
            return
        if output_headers:
            try:
                body = json.loads(self.__message_text)
            except json.decoder.JSONDecodeError:
                body = self.__message_text
            response = {
                'headers': dict(self.__response_headers),
                'body': body
            }
            click.echo(json.dumps(response))
        else:
            click.echo(self.__message_text)

    def print(self, print_status=True, output_headers=False):
        if print_status:
            if 400 <= self.__http_status_code:
                color = 'red'
            else:
                color = 'green'
            status_msg = http.client.responses[self.__http_status_code]
            status_text = str(self.__http_status_code) + ' ' + status_msg
            click.echo(click.style(
                status_text,
                fg=color),
                err=True
            )
        self.print_message(output_headers)

    def get_request_time(self):
        return self.__request_body.get('time')

    @staticmethod
    def build_from_requests_result(result, message=None, request_body=None):
        message = message if message is not None else result.text
        return PlatformResponse(result.text,
                                result.status_code,
                                message,
                                request_body=request_body,
                                response_headers=result.headers)


def login(login_id, password):
    # TODO: move this to core
    authorization = config.load()['default'].get('authorization')
    if not authorization:
        raise click.ClickException('Authorization Id is required.')
    pool_id, client_id = decode_cognito_setting(authorization)
    try:
        response = client.initiate_auth(
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': login_id,
                'PASSWORD': password
            },
            ClientId=client_id
        )
    except client.exceptions.NotAuthorizedException:
        raise click.ClickException('Password Incorrect')
    except boto_exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'UserNotFoundException':
            raise click.ClickException(f'Account with id({login_id}) is not found.')

        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise click.ClickException(e.response['Error']['Message'])

        # TODO: Add error for expired refresh token.
        else:
            raise e

    return response


def change_password(old_password, new_password, access_token):
    try:
        client.change_password(
            PreviousPassword=old_password,
            ProposedPassword=new_password,
            AccessToken=access_token
        )
    except boto_exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'InvalidPasswordException':
            error_message_all = str(e.response['Error']['Message'])
            result = re.match('(.*: )(?P<message>.*$)', error_message_all)
            if result is not None:
                raise click.ClickException(result.group('message'))
            else:
                raise click.ClickException('Invalid Password.')
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            raise click.ClickException(e.response['Error']['Message'])
        elif e.response['Error']['Code'] == 'LimitExceededException':
            raise click.ClickException(e.response['Error']['Message'])
        else:
            raise e
    except boto_exceptions.ParamValidationError as e:
        raise e


def create_bot(filepath,
               name=None,
               message=None,
               nlu_url=None,
               nlu_api_key=None):
    with open(filepath, 'rb') as f:
        encoded_file = base64.b64encode(f.read()).decode('utf-8')
    body = {
        'file': encoded_file,
        'name': name,
        'message': message,
        'nluUrl': nlu_url,
        'nluApiKey': nlu_api_key
    }
    body = {k: v for k, v in body.items() if v is not None}
    r = api_session().post(build_url(BOT_API_PATH), json=body)
    return PlatformResponse.build_from_requests_result(r)


def update_bot(bot_id,
               filepath=None,
               name=None,
               message=None,
               nlu_url=None,
               nlu_api_key=None):
    body = {
        'name': name,
        'message': message,
        'nluUrl': nlu_url,
        'nluApiKey': nlu_api_key
    }

    if filepath:
        with open(filepath, 'rb') as f:
            body['file'] = base64.b64encode(f.read()).decode('utf-8')

    body = {k: v for k, v in body.items() if v is not None}

    r = api_session().put(
        build_url(BOT_API_PATH, bot_id),
        json=body)
    return PlatformResponse.build_from_requests_result(r)


def list_bots():
    r = api_session().get(build_url(BOT_API_PATH))
    return PlatformResponse.build_from_requests_result(r)


def get_bot(bot_id, zipfile_path):
    api_path = build_url(BOT_API_PATH, bot_id)
    if zipfile_path:
        api_path = api_path + '?include_scenario=true'

    r = api_session().get(api_path)
    res = PlatformResponse.build_from_requests_result(r)
    if zipfile_path:
        with open(zipfile_path, 'wb') as f:
            f.write(base64.b64decode(res.get_response_body()['file']))
    return res


def delete_bot(bot_id):
    r = api_session().delete(build_url(BOT_API_PATH, bot_id))
    return PlatformResponse.build_from_requests_result(r)


def generate_ask_url(bot_id, base_url=None):
    return build_url(BOT_API_PATH, bot_id, 'ask', base_url=base_url)


def ask_bot(
        bot_id,
        api_key,
        user_id,
        utterance,
        topic=None,
        metadata=None,
        log_level=None,
        locale=None,
):
    """
    Returns:
      (decode_response_text, unicode_response_text, request_time)
    """
    request_time = get_local_time(locale)
    payload = {
        "locale": locale,
        "time": request_time,
        "userId": user_id,
        "utterance": utterance,
    }
    if log_level is not None:
        payload['config'] = {"logLevel": log_level}
    if topic is not None:
        payload['topic'] = topic
    if metadata is not None:
        payload['metadata'] = metadata

    r = api_session(api_key=api_key).post(
        generate_ask_url(bot_id),
        json=payload)

    return PlatformResponse.build_from_requests_result(
        r,
        request_body=payload)


def debug_bot(bot_id, api_key, user_id='None'):
    # FIXME: user_id should be required argument.
    r = api_session(api_key=api_key).post(
        build_url(BOT_API_PATH, bot_id, 'debug'),
        json={'userId': user_id})
    return PlatformResponse.build_from_requests_result(r)


def create_api_key(bot_id,
                   expiration_days,
                   max_api_calls,
                   description):
    request_body = {
        'expirationDays': expiration_days,
        'maxApiCalls': max_api_calls,
        'description': description,
    }

    r = api_session().post(
        build_url(BOT_API_PATH, bot_id, 'api-keys'),
        json=request_body)
    return PlatformResponse.build_from_requests_result(r)


def list_api_keys(bot_id):
    r = api_session().get(
        build_url(BOT_API_PATH, bot_id, 'api-keys'))
    return PlatformResponse.build_from_requests_result(r)


def get_api_key(bot_id, api_key):
    r = api_session().get(
        build_url(BOT_API_PATH, bot_id, 'api-keys', api_key))
    return PlatformResponse.build_from_requests_result(r)


def update_api_key(bot_id,
                   api_key,
                   description):
    request_body = {}

    if description is not None:
        request_body['description'] = description

    r = api_session().put(
        build_url(BOT_API_PATH, bot_id, 'api-keys', api_key),
        json=request_body)
    return PlatformResponse.build_from_requests_result(r)


def delete_api_key(bot_id, api_key):
    r = api_session().delete(
        build_url(BOT_API_PATH, bot_id, 'api-keys', api_key))
    return PlatformResponse.build_from_requests_result(r)


def run_bot(bot_id, update):
    api_path = build_url(BOT_API_PATH, bot_id, 'run')
    if update:
        api_path = api_path + '?update=true'

    r = api_session().post(api_path)
    return PlatformResponse.build_from_requests_result(r)


def stop_bot(bot_id):
    r = api_session().post(
        build_url(BOT_API_PATH, bot_id, 'stop'))
    return PlatformResponse.build_from_requests_result(r)


def encode_cognito_setting(pool_id, client):
    connected_text = ','.join([pool_id, client])
    encoded_text = base64.encodebytes(connected_text.encode('ascii'))
    return encoded_text


def decode_cognito_setting(encoded_cognito_setting):
    """
    Returns:
      (pool_id, client_id)
    """
    if type(encoded_cognito_setting) is str:
        encoded_cognito_setting = encoded_cognito_setting.encode('ascii')
    try:
        decoded_text = base64.decodebytes(
            encoded_cognito_setting).decode('ascii')
    except base64.binascii.Error:
        raise click.ClickException('Invalid Authorization Id Format')
    if decoded_text.count(',') != 1:
        raise click.ClickException('Invalid Authorization Id')
    return tuple(decoded_text.strip().split(','))


def get_local_time(locale):
    result = re.match('(?P<lang>.*)[_|-](?P<code>.*)', locale)
    country_code = result.group('code')
    tz_dict = pytz.country_timezones
    tz = tz_dict.get(country_code)
    return datetime.now(timezone(tz[0])).isoformat(timespec='seconds')


def get_bot_logs(start_date=None,
                 end_date=None,
                 limit=None,
                 offset=None,
                 bot_id=None,
                 api_key_id=None):
    params = {'start': start_date, 'end': end_date,
              'limit': limit, 'offset': offset,
              'bot_id': bot_id, 'api_key_id': api_key_id}
    r = api_session().get(
        build_url(BOT_API_PATH, 'logs', 'dialogues'),
        params=params)
    return PlatformResponse.build_from_requests_result(r)


def get_bot_traffics(aggregation,
                     start_date=None,
                     end_date=None,
                     bot_id=None,
                     api_key_id=None):
    params = {'aggregation': aggregation,
              'start': start_date, 'end': end_date,
              'bot_id': bot_id, 'api_key_id': api_key_id}
    r = api_session().get(
        build_url(BOT_API_PATH, 'logs', 'traffics'),
        params=params)
    return PlatformResponse.build_from_requests_result(r)


def get_bot_topics(aggregation,
                   start_date=None,
                   end_date=None,
                   bot_id=None,
                   api_key_id=None):
    params = {'aggregation': aggregation,
              'start': start_date, 'end': end_date,
              'bot_id': bot_id, 'api_key_id': api_key_id}
    r = api_session().get(
        build_url(BOT_API_PATH, 'logs', 'topics'),
        params=params)
    return PlatformResponse.build_from_requests_result(r)
