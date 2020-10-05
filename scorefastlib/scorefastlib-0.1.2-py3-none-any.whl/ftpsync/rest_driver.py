"""Data Configuration Util"""
from ftpsync.constants import Common
from datatransfer.rest_client import RestClient
from ftpsync.settings import (job_user, job_password, config_url, process_log_url)


class DataConfigUtil:
    """Data configuration DAO"""

    @staticmethod
    def get_config_with_ftp_credentials(interval):
        res = RestClient.get(url=config_url,
                             auth={'user': job_user,
                                   'password': job_password}).json()
        results = []
        if res.get('status') == 'success':
            results = res['data']
        return results

    @staticmethod
    def get_process_status_by_config_id(config_id):
        file_names = []
        res = RestClient.get(url=process_log_url + "config/" + str(config_id),
                             auth={'user': job_user,
                                   'password': job_password}).json()
        if res.get('status') == 'success':
            for item in res['data']:
                file_names.append(item.get('source_file'))
        return file_names

    @staticmethod
    def add_process_key_status(config_id, file):
        inserted_id = None
        input = dict()
        input['config_id'] = config_id
        input['process_key'] = str(config_id) + "-" + file
        input['source_file'] = file
        input['status'] = Common.process_status_0.value
        res = RestClient.post(url=process_log_url,
                              auth={'user': job_user,
                                    'password': job_password},
                              data=input).json()
        if res.get('status') == 'success':
            inserted_id = res.get('data')['id']
        return inserted_id

    @staticmethod
    def update_process_key_status(process_log_id, success):
        input_msg = dict()
        input_msg['status'] = success['status']
        input_msg['status_msg'] = success['msg']
        input_msg['dest_file'] = success['dest_path']
        res = RestClient.put(url=process_log_url + str(process_log_id) + "/",
                             auth={'user': job_user,
                                   'password': job_password},
                             data=input_msg).json()
        return res
