"""
S3 Processor
"""
import os
import socket
import time

import boto3
from boto3.s3.transfer import S3Transfer

from datatransfer.util import Utility
from ftpsync.constants import Common
from ftpsync.rest_driver import DataConfigUtil
from ftpsync.ftp_util import FTPUtility
from ftpsync.settings import ( job_user, job_password)


class S3Processor:
    """Takes care of S3 files upload and download"""

    @staticmethod
    def put_files(config, file):
        """Upload local files to S3"""
        success = {}
        local_file_path = ''
        compress_file = ''
        dest_path = ''
        try:
            s3_conf = Utility.__authenticate_request__(job_user,
                                                       job_password)
            access_key = s3_conf.get('access_key')
            secret_key = s3_conf.get('secret_key')
            bucket_name = s3_conf.get('bucket')
            date_format = s3_conf.get('namespace')[2:]
            client_id = str(config['client_id'])
            transfer = S3Transfer(boto3.client('s3', aws_access_key_id=access_key,
                                               aws_secret_access_key=secret_key))
            local_file_path = str(client_id) + "/" + str(config['config_id']) + "/" + file
            local_file_dir = local_file_path[:local_file_path.rfind('/')]
            # compress file
            compress_file = Utility.__compress_file__(local_file_path, local_file_dir, "gz")
            # upload file
            file_name = os.path.basename(compress_file)
            hostname_unixtime = socket.gethostname() + "_" + str(
                int(time.time()))
            file_name = hostname_unixtime + "_" + file_name
            dest_path = client_id + "/" + config['dest'] + "/" + date_format + "/" + file_name
            # upload file
            transfer.upload_file(compress_file, bucket_name, dest_path)
            # build success
            success['status'] = Common.process_status_2.value
            success['msg'] = "Success"
            success['source_path'] = file
            success['dest_path'] = dest_path

        except Exception as ex:
            success['status'] = Common.process_status_1.value
            success['msg'] = str(ex)
            success['source_path'] = file
            success['dest_path'] = dest_path
        finally:
            FTPUtility.delete_file(local_file_path)
            FTPUtility.delete_file(compress_file)
        return success

    def get_files(self, config):
        """Download files from S3"""
        s3_conf = Utility.__authenticate_request__(job_user, job_password)
        access_key = s3_conf.get('access_key')
        secret_key = s3_conf.get('secret_key')
        bucket_name = s3_conf.get('bucket')
        client = boto3.client('s3', aws_access_key_id=access_key,
                              aws_secret_access_key=secret_key)
        transfer = S3Transfer(client)
        # get list of files from s3
        list_files = []
        response = client.list_objects(Bucket=bucket_name,
                                       Prefix=config['client_id'] + "/" + config['source'])
        for content in response.get('Contents', []):
            list_files.append(content.get('Key'))

        processed_files_list = DataConfigUtil.get_process_status_by_config_id(config['config_id'])
        unprocessed_files = [x for x in list_files if x not in processed_files_list]
        files = []
        # download
        for unprocessed_file in unprocessed_files:
            f = unprocessed_file.replace("/", "|")
            transfer.download_file(bucket_name, unprocessed_file, f)
            files.append(unprocessed_file)

        return files
