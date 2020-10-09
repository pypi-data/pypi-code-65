import csv
import gzip
import http
import json
import logging
import mimetypes
import os
import time

import click

from urllib.parse import urljoin
from cotoba_cli import platform
from cotoba_cli.error import ApiResponseError
from cotoba_cli.util import api_session

logger = logging.getLogger(__name__)


ENDPOINT_URL_MAP = {
    'model_type': 'nlu/model-type',
    'apy_keys': 'nlu/models',
    'inferences': 'nlu/models',
    'model_metadata': 'nlu/models',
    'remaining_resources': 'nlu/remaining',
    'training_job': 'nlu/models',
    'training_data': 'nlu/training-data',
    'slot_dictionary': 'nlu/slot-dictionary'
}

TRAINING_DATA_SIZE_LIMIT = 2 * 1024 * 1024
SLOT_DICTIONARY_SIZE_LIMIT = 100 * 1024 * 1024


def create_training_data(auth, name, filepath,
                         description='None', limit=TRAINING_DATA_SIZE_LIMIT,
                         endpoint_url=None):
    error_msg = check_training_data(filepath, limit)
    if error_msg is not None:
        raise click.ClickException(error_msg)

    r = api_session().post(
        urljoin(endpoint_url, ENDPOINT_URL_MAP['training_data']),
        json={
            'name': name,
            'description': description
        })
    res = platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )
    r_json = res.get_response_body()
    if 'uploadUrl' in r_json:
        upload_url = r_json['uploadUrl']
        try:
            with open(filepath, 'rb') as f:
                api_session(authorization=False).put(upload_url, data=f)
        except OSError as e:
            raise click.ClickException(str(e))
        res.message = json.dumps({
            'trainingDataId': r_json['trainingDataId']
        })
    # Wait upload complete.
    retry_count = 5
    for i in range(retry_count):
        try:
            read_result = read_training_data(
                auth, r_json['trainingDataId'], endpoint_url=endpoint_url)
            if read_result.http_status_code == http.HTTPStatus.OK:
                break
        except ApiResponseError as e:
            if e.status_code != 404:
                raise Exception(e)
            elif i + 1 == retry_count:
                raise click.ClickException(
                    f'Training data creation failed. '
                    f'Training data id: {r_json["trainingDataId"]}.')
            time.sleep(2)
    return res


def check_training_data(filepath, limit=TRAINING_DATA_SIZE_LIMIT):
    """
    訓練データのファイルフォーマットチェックを行う。
    Parameters
        filepath: str
            チェック対象のファイルパス
        limit: int
            ファイルの許容サイズ
    Returns
        チェックに失敗した時: エラーメッセージ
        問題ないとき: None
    """

    training_data = None
    mime = None
    try:
        if os.path.getsize(filepath) > limit:
            return 'File size limit exceeded for uploading.'
        mime = mimetypes.guess_type(filepath)
        if 'gzip' in mime:
            with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                training_data = json.load(f)
        elif 'application/json' in mime:
            with open(filepath, 'r', encoding='utf-8') as f:
                training_data = json.load(f)
        else:
            return 'The file format must be "json" or "gzip".'
    except json.JSONDecodeError as e:
        return str(e)
    except FileNotFoundError as e:
        return str(e)

    if 'training' not in training_data:
        return 'The key "{}" is required for the file.'.format('training')

    valid_keys = ['training', 'validation']
    for key in training_data.keys():
        if key not in valid_keys:
            return 'The key of "{0}" is invalid. The key "{1}" is valid.' \
                .format(key, valid_keys)

        error_msg = 'Format error of data {0} of key "{1}": {2}'

        for line_number, data in enumerate(training_data[key]):

            if 'text' not in data:
                return error_msg.format(
                    line_number, key, 'There must be "text" in request.')
            if not isinstance(data['text'], str):
                return error_msg.format(
                    line_number, key,
                    'The type of "text" is invalid. The type "str" is valid.')

            if 'intent' not in data:
                return error_msg.format(
                    line_number, key, 'There must be "intent" in request.')
            if not isinstance(data['intent'], list):
                return error_msg.format(
                    line_number, key,
                    'The type of "intent" is invalid. '
                    'The type "[str]" is valid.')

            for intent in data['intent']:
                if not isinstance(intent, str):
                    return error_msg.format(
                        line_number, key,
                        'The type of "intent" is invalid. '
                        'The type "[str]" is valid.')

            if 'slot' not in data:
                return error_msg.format(
                    line_number, key, 'There must be "slot" in request.')
            if not isinstance(data['slot'], list):
                return error_msg.format(
                    line_number, key,
                    'The type of "slot" is invalid. '
                    'The type "list" is valid.')

            for slot in data['slot']:
                if 'type' not in slot:
                    return error_msg.format(
                        line_number, key,
                        'There must be "type" in request of "slot".')
                if not isinstance(slot['type'], str):
                    return error_msg.format(
                        line_number, key,
                        'The type of "type" is invalid. '
                        'The type "str" is valid.')
                if 'start' not in slot:
                    return error_msg.format(
                        line_number, key,
                        'There must be "start" in request of "slot".')
                if not isinstance(slot['start'], int):
                    return error_msg.format(
                        line_number, key,
                        'The type of "start" is invalid. '
                        'The type "int" is valid.')
                if 'end' not in slot:
                    return error_msg.format(
                        line_number, key,
                        'There must be "end" in request of "slot".')
                if not isinstance(slot['end'], int):
                    return error_msg.format(
                        line_number, key,
                        'The type of "end" is invalid. '
                        'The type "int" is valid.')
    return None


def update_training_data(auth, training_data_id, name, description,
                         endpoint_url=None):
    if not any([name, description]):
        # TODO: this error should be raised in cli section.
        raise click.UsageError(
            'Error: Please specify at least "--name" or "--description".\n')
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['training_data'])
    headers = {
        'Authorization': auth.id_token,
        'Content-Type': 'application/json'
    }
    param = {
        'name': name,
        'description': description
    }
    param = {k: v for k, v in param.items() if v is not None}
    r = api_session().put(
        '{}/{}'.format(endpoint_url, training_data_id),
        json.dumps(param),
        headers=headers)
    return platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )


def delete_training_data(auth, training_data_id,
                         endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['training_data'])
    headers = {
        'Authorization': auth.id_token,
    }
    r = api_session().delete(
        '{}/{}'.format(endpoint_url, training_data_id),
        headers=headers)
    r.raise_for_status
    return platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )


def read_training_data(auth, training_data_id,
                       endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['training_data'])
    headers = {
        'Authorization': auth.id_token,
    }
    r = api_session().get(
        '{}/{}'.format(endpoint_url, training_data_id),
        headers=headers)
    res = platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )
    return res


def list_training_data(auth,
                       endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['training_data'])
    headers = {
        'Authorization': auth.id_token,
    }
    r = api_session().get(
        endpoint_url,
        headers=headers)
    res = platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['trainingDataId'])
    )
    return res


def list_model_type(endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['model_type'])
    r = api_session().get(endpoint_url)
    r.raise_for_status

    return platform.PlatformResponse.build_from_requests_result(r)


def read_model_type(model_type_name, endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['model_type'])
    r = api_session().get('{}/{}'.format(endpoint_url, model_type_name))
    return platform.PlatformResponse.build_from_requests_result(r)


def create_slot_dictionary(auth, name, filepath,
                           description='None',
                           limit=SLOT_DICTIONARY_SIZE_LIMIT,
                           endpoint_url=None):
    error_msg = check_slot_dictionary(filepath, limit)
    if error_msg is not None:
        raise click.ClickException(error_msg)

    headers = {
        'Authorization': auth.id_token,
        'Content-Type': 'application/json'
    }
    r = api_session().post(
        urljoin(endpoint_url, ENDPOINT_URL_MAP['slot_dictionary']),
        json.dumps({
            'name': name,
            'description': description
        }),
        headers=headers)
    res = platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )
    r_json = res.get_response_body()
    if 'uploadUrl' in r_json:
        upload_url = r_json['uploadUrl']
        try:
            with open(filepath, 'rb') as f:
                api_session(authorization=False).put(upload_url, data=f)
        except OSError as e:
            click.ClickException(str(e))
        res.message = json.dumps({
            'slotDictionaryId': r_json['slotDictionaryId']
        })
    # Wait upload complete.
    retry_count = 5
    for i in range(retry_count):
        try:
            read_result = read_slot_dictionary(
                auth, r_json['slotDictionaryId'], endpoint_url=endpoint_url)
            if read_result.http_status_code == http.HTTPStatus.OK:
                break
        except ApiResponseError as e:
            if e.status_code != 404:
                raise Exception(e)
            elif i + 1 == retry_count:
                raise click.ClickException(
                    f'Slot dictionary creation failed. '
                    f'Slot dictionary id: {r_json["slotDictionaryId"]}.')
            time.sleep(2)
    return res


def check_slot_dictionary(filepath, limit=SLOT_DICTIONARY_SIZE_LIMIT):
    """
    slot辞書のファイルフォーマットチェックを行う。
    Parameters
        filepath: str
            チェック対象のファイルパス
        limit: int
            ファイルの許容サイズ
    Returns
        チェックに失敗した時: エラーメッセージ
        問題ないとき: None
    """

    try:
        if os.path.getsize(filepath) > limit:
            return 'File size limit exceeded for uploading.'
    except FileNotFoundError as e:
        return str(e)

    slot_dictionary_file = None
    try:
        mime = mimetypes.guess_type(filepath)
        if 'gzip' in mime:
            slot_dictionary_file = gzip.open(filepath, 'rt', encoding='utf-8')
        else:
            slot_dictionary_file = open(filepath, 'r', encoding='utf-8')
        slot_dictionary_csv = csv.reader(slot_dictionary_file, delimiter='\t')
        for line_number, line in enumerate(slot_dictionary_csv):
            if len(line) == 2:
                continue
            elif len(line) == 3:
                if line[2].startswith('r'):
                    continue
                else:
                    return f'Format error of line {line_number + 1}. ' \
                           f'Column 3 starts with "r".'
            else:
                return f'Format error of line {line_number + 1}. ' \
                       f'2 column "TSV" is valid.'
    finally:
        slot_dictionary_file.close()

    return None


def read_slot_dictionary(auth, slot_dictionary_id,
                         endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['slot_dictionary'])
    headers = {
        'Authorization': auth.id_token,
    }
    r = api_session().get(
        '{}/{}'.format(endpoint_url, slot_dictionary_id),
        headers=headers)

    res = platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )
    return res


def delete_slot_dictionary(auth, slot_dictionary_id,
                           endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['slot_dictionary'])
    headers = {
        'Authorization': auth.id_token,
    }
    r = api_session().delete(
        '{}/{}'.format(endpoint_url, slot_dictionary_id),
        headers=headers)
    return platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )


def list_slot_dictionaries(auth,
                           endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['slot_dictionary'])
    headers = {
        'Authorization': auth.id_token,
    }
    r = api_session().get(
        endpoint_url,
        headers=headers)
    res = platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['slotDictionaryId'])
    )
    return res


def update_slot_dictionary(auth, slot_dictionary_id, name, description,
                           endpoint_url=None):
    if not any([name, description]):
        # TODO: The error should be raised by cli.
        raise click.UsageError('Error: Please specify at least "--name" or "--description".')
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['slot_dictionary'])
    headers = {
        'Authorization': auth.id_token,
        'Content-Type': 'application/json'
    }
    param = {
        'name': name,
        'description': description
    }
    param = {k: v for k, v in param.items() if v is not None}
    r = api_session().put(
        '{}/{}'.format(endpoint_url, slot_dictionary_id),
        json.dumps(param),
        headers=headers)
    return platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )


def create_model(auth,
                 training_data_id,
                 model_type_name,
                 slot_dictionary_id,
                 name,
                 description,
                 file_path,
                 hyper_parameters,
                 original_model_id,
                 wait,
                 endpoint_url=None):
    param = {
        'trainingDataId': training_data_id,
        'modelTypeName': model_type_name,
        'name': name,
        'slotDictionaryId': slot_dictionary_id,
        'description': description,
        'originalModelId': original_model_id
    }
    # Removes None value from param.
    param = {k: v for k, v in param.items() if v is not None}

    param['hyperParameters'] = {}
    if file_path is not None:
        try:
            with open(file_path) as f:
                param['hyperParameters'] = json.load(f)
        except (json.JSONDecodeError,
                FileNotFoundError,
                IsADirectoryError) as e:
            raise click.ClickException(str(e))
    elif hyper_parameters is not None:
        try:
            param['hyperParameters'] = json.loads(hyper_parameters)
        except json.JSONDecodeError as e:
            raise click.ClickException(str(e))

    headers = {
        'Authorization': auth.id_token,
        'Content-Type': 'application/json'
    }
    r = api_session().post(
        urljoin(endpoint_url, ENDPOINT_URL_MAP['training_job']),
        json.dumps(param),
        headers=headers)
    res = platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['modelId', 'message'])
    )
    # Wait training complete.
    if wait:
        r_json = res.get_response_body()
        wait_for_model_status(
            auth,
            r_json['modelId'],
            'TrainingCompleted',
            endpoint_url)
    return res


def read_model(auth, model_id,
               endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['model_metadata'])
    headers = {
        'Authorization': auth.id_token
    }
    r = api_session().get(
        '{}/{}'.format(endpoint_url, model_id),
        headers=headers)
    res = platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r,
            ['modelId', 'trainingDataId', 'message'])
    )
    return res


def update_model(auth, model_id, name, description,
                 endpoint_url=None):
    if not any([name, description]):
        # TODO: this error should be raised in cli section.
        raise click.UsageError('Error: Please specify at least "--name" or "--description".')
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['model_metadata'])
    headers = {
        'Authorization': auth.id_token
    }
    param = {
        'name': name,
        'description': description
    }
    param = {k: v for k, v in param.items() if v is not None}
    r = api_session().put(
        '{}/{}'.format(endpoint_url, model_id),
        json.dumps(param),
        headers=headers)
    return platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )


def delete_model(auth, model_id,
                 endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['model_metadata'])
    headers = {
        'Authorization': auth.id_token
    }
    r = api_session().delete(
        '{}/{}'.format(endpoint_url, model_id),
        headers=headers)
    return platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )


def list_models(auth,
                endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['training_job'])
    headers = {
        'Authorization': auth.id_token,
    }
    r = api_session().get(
        endpoint_url,
        headers=headers)
    res = platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['modelId', 'trainingDataId'])
    )
    return res


def create_endpoint(auth,
                    model_id,
                    min_capacity,
                    max_capacity,
                    initial_instance_count,
                    wait,
                    slot_dictionary_id=None,
                    endpoint_url=None):
    headers = {
        'Authorization': auth.id_token,
        'Content-Type': 'application/json'
    }
    params = {
        'minCapacity': min_capacity,
        'maxCapacity': max_capacity,
        'initialInstanceCount': initial_instance_count
    }
    if slot_dictionary_id:
        params['slotDictionaryId'] = slot_dictionary_id
    r = api_session().put(
        '{}/{}/endpoint'.format(
            urljoin(endpoint_url, ENDPOINT_URL_MAP['inferences']), model_id),
        json.dumps(params),
        headers=headers)
    res = platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['endpointId', 'message'])
    )
    # Wait create complete.
    if wait:
        wait_for_model_status(
            auth,
            model_id,
            'EndpointInService',
            endpoint_url,
            retry_count=15)
    return res


def update_endpoint(auth,
                    model_id,
                    min_capacity,
                    max_capacity,
                    desired_instance_count,
                    wait,
                    endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['inferences'])
    headers = {
        'Authorization': auth.id_token,
        'Content-Type': 'application/json'
    }
    params = {
        'minCapacity': min_capacity,
        'maxCapacity': max_capacity,
        'desiredInstanceCount': desired_instance_count
    }
    r = api_session().put(
        '{}/{}/endpoint/update'.format(endpoint_url, model_id),
        json.dumps(params),
        headers=headers)
    res = platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['endpointId', 'message'])
    )
    # Wait update complete.
    if wait:
        wait_for_model_status(
            auth,
            model_id,
            'EndpointInService',
            endpoint_url,
            retry_count=15)
    return res


def get_inference_logs(auth,
                       model_id,
                       api_key_id,
                       start_date,
                       end_date,
                       limit,
                       offset,
                       endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['inferences'])
    headers = {
        'Authorization': auth.id_token,
        'Content-Type': 'application/json'
    }
    query_param = {}
    query_param['api-key-id'] = api_key_id
    query_param['start'] = start_date
    query_param['end'] = end_date
    query_param['limit'] = limit
    query_param['offset'] = offset
    query_param = {k: v for k, v in query_param.items() if v is not None}
    r = api_session().get(
        '{}/{}/endpoint/logs'.format(endpoint_url, model_id),
        params=query_param, headers=headers)
    return platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )


def read_intent(auth,
                model_id,
                endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['inferences'])
    headers = {
        'Authorization': auth.id_token
    }
    r = api_session().get(
        '{}/{}/intent'.format(endpoint_url, model_id),
        headers=headers)
    return platform.PlatformResponse.build_from_requests_result(
        r,
        detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )


def read_slot(auth,
              model_id,
              endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['inferences'])
    headers = {
        'Authorization': auth.id_token
    }
    r = api_session().get(
        '{}/{}/slot'.format(endpoint_url, model_id),
        headers=headers)
    return platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )


def read_dictionary_label(auth,
                          model_id,
                          endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['inferences'])
    headers = {
        'Authorization': auth.id_token
    }
    r = api_session().get(
        '{}/{}/dictionary-label'.format(endpoint_url, model_id),
        headers=headers)
    return platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )


def delete_endpoint(auth,
                    model_id,
                    endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['inferences'])
    headers = {
        'Authorization': auth.id_token
    }
    r = api_session().delete(
        '{}/{}/endpoint'.format(endpoint_url, model_id),
        headers=headers)
    return platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )


def inference(auth,
              utterance,
              model_id,
              api_key,
              slot_dic='',
              endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['inferences'])
    headers = {
        'x-api-key': api_key
    }
    body = {'utterance': utterance}
    if slot_dic != '':
        try:
            if os.path.isfile(slot_dic):
                with open(slot_dic) as f:
                    slots = json.load(f)
            else:
                slots = json.loads(slot_dic)
        except json.JSONDecodeError as e:
            raise click.ClickException(f'Cannot load slot dictionary as json format: {e}')

        for sl in slots:
            if not isinstance(sl, str) or not isinstance(slots[sl], list):
                raise click.ClickException(
                    'The json format of slot dictionary you specified is invalid.\n'
                    'Valid format: {key: [value1, value2, ...]}.\n'
                    'e.g., {"駅": ["渋谷", "表参道"], "年号": ["令和"]}',)
        body['slotExpressions'] = slots

    r = api_session().post(
        '{}/{}/endpoint'.format(endpoint_url, model_id),
        json.dumps(body),
        headers=headers)
    return platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )


def get_endpoint_url(auth,
                     endpoint_id,
                     api_key='',
                     endpoint_url=None):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['inferences'])
    headers = {
        'x-api-key': api_key
    }
    url = '{}/{}/endpoint'.format(endpoint_url, endpoint_id)
    r = api_session().post(
        url,
        json.dumps({'utterance': 'テスト'}),
        headers=headers)
    res = platform.PlatformResponse.build_from_requests_result(
        r,
        message='None')
    r_json = res.get_response_body()
    if 'intents' in r_json:
        res.message = url
    return res


def read_remaining_resources(auth, endpoint_url=None):
    endpoint_url = urljoin(
        endpoint_url, ENDPOINT_URL_MAP['remaining_resources'])
    headers = {
        'Authorization': auth.id_token
    }
    r = api_session().get(
        '{}/{}'.format(endpoint_url, auth.sub),
        headers=headers)
    return platform.PlatformResponse.build_from_requests_result(r)


def create_api_key(auth,
                   model_id,
                   description,
                   endpoint_url):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['apy_keys'])
    headers = {
        'Authorization': auth.id_token,
        'Content-Type': 'application/json'
    }
    params = {
        'description': description
    }
    r = api_session().post(
        '{}/{}/api-keys'.format(endpoint_url, model_id),
        json.dumps(params),
        headers=headers)
    return platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )


def list_api_keys(auth, model_id, endpoint_url):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['apy_keys'])
    headers = {
        'Authorization': auth.id_token
    }
    r = api_session().get(
        '{}/{}/api-keys'.format(endpoint_url, model_id),
        headers=headers)
    return platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )


def read_api_key(auth, model_id, api_key_id, endpoint_url):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['apy_keys'])
    headers = {
        'Authorization': auth.id_token
    }
    r = api_session().get(
        '{}/{}/api-keys/{}'.format(endpoint_url, model_id, api_key_id),
        headers=headers)
    return platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )


def update_api_key(auth,
                   model_id,
                   api_key_id,
                   description,
                   endpoint_url):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['apy_keys'])
    headers = {
        'Authorization': auth.id_token,
        'Content-Type': 'application/json'
    }
    params = {
        'description': description
    }
    r = api_session().put(
        '{}/{}/api-keys/{}'.format(endpoint_url, model_id, api_key_id),
        json.dumps(params),
        headers=headers)
    return platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )


def delete_api_key(auth, model_id, api_key_id, endpoint_url):
    endpoint_url = urljoin(endpoint_url, ENDPOINT_URL_MAP['apy_keys'])
    headers = {
        'Authorization': auth.id_token
    }
    r = api_session().delete(
        '{}/{}/api-keys/{}'.format(endpoint_url, model_id, api_key_id),
        headers=headers)
    return platform.PlatformResponse.build_from_requests_result(
        r,
        message=detach_user_id_from_resource_id(
            auth.sub, r, ['message'])
    )


def detach_user_id_from_resource_id(user_id, response, keys):
    """
    keys で指定した response[key] の値の resource_id 部分から user_id の値を削除する。
    Parameters
        user_id: str
            ユーザID
        response: dict or dictのリスト
            APIからのレスポンス
        keys: list
            マスクするresponseのキー
    Returns
        ユーザIDをマスクした結果
    """
    try:
        response = json.loads(response.text)
    except json.JSONDecodeError:
        return response.text
    original_response_type_is_not_list = type(response) is not list
    if not isinstance(response, list):
        response = [response]
    for r in response:
        for key in keys:
            if key in r:
                # 最初に一致するユーザID(システムで付与したユーザID)を削除
                r[key] = r[key].replace(user_id + '-', '', 1)
    if original_response_type_is_not_list:
        response = response[0]
    return json.dumps(response)


def wait_for_model_status(
        auth,
        model_id,
        expected_status,
        endpoint_url,
        retry_count=60,
        sleep_seconds=60):
    error_msg = f'Timeout has occurred. ' \
                f'Please check the status of {model_id} after a while. ' \
                f'If the status is not {expected_status}, ' \
                f'there may be a problem.'
    for i in range(retry_count):
        read_result = read_model(
            auth, model_id, endpoint_url=endpoint_url)
        read_r_json = read_result.get_response_body()
        if read_r_json['status'] == expected_status:
            break
        if 'Failed' in read_r_json['status']:
            raise click.ClickException(error_msg)
        if i + 1 == retry_count:
            raise click.ClickException(error_msg)
        time.sleep(sleep_seconds)
