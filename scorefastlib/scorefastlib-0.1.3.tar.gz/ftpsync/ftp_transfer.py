"""FTP Transfer main job"""

import time
import datetime
import copy

from ftpsync.constants import Common
from ftpsync.rest_driver import DataConfigUtil
from ftpsync.ftp_processor import FTPProcessor
from ftpsync.ftp_util import FTPUtility
from ftpsync.s3_processor import S3Processor
from ftpsync.sftp_processor import SFTPProcessor


class FTPTransfer:
    """Executes job basis on client configuration. Supports FTP and S3 data source"""

    @staticmethod
    def process(interval):
        """Process job on interval basis"""

        log_events = {}
        log_events['interval'] = interval
        log_events['job_id'] = str(int(time.time()))
        log_events['job_datetime'] = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        log_job_events = copy.deepcopy(log_events)
        log_job_events['job_status'] = 'started'
        try:

            FTPUtility.log_event(Common.logger_tag_info.value, log_job_events)
            config_list = DataConfigUtil.get_config_with_ftp_credentials(interval)
            if len(config_list) == 0:
                log_events['ftptransfer_config'] = 'None'
                FTPUtility.log_event(Common.logger_tag_info.value, log_events)

            for config in config_list:
                print(config)
                log_events['ftptransfer_config'] = config
                list_files = []
                try:
                    download_processor = FTPTransfer.get_processor(config['source_type'])
                    list_files = download_processor.get_files(config)
                    upload_processor = FTPTransfer.get_processor(config['dest_type'])
                except Exception as ex:
                    log_events['ftptransfer_download'] = str(ex)
                    FTPUtility.log_event(Common.logger_tag_error.value, log_events)
                    continue

                for file in list_files:
                    try:
                        # log file processing status
                        record_id = DataConfigUtil.add_process_key_status(config['config_id'],
                                                                             file)
                        if record_id is None:
                            continue
                        success = upload_processor.put_files(config, file)
                        log_events['ftptransfer_status'] = success
                        FTPUtility.log_event(Common.logger_tag_info.value, log_events)
                        DataConfigUtil.update_process_key_status(record_id, success)
                    except Exception as ex:
                        log_events['ftptransfer_upload'] = str(ex)
                        FTPUtility.log_event(Common.logger_tag_error.value, log_events)

        except Exception as ex:
            log_events['ftptransfer_process'] = str(ex)
            FTPUtility.log_event(Common.logger_tag_error.value, log_events)
        finally:
            log_job_events['job_status'] = 'completed'
            FTPUtility.log_event(Common.logger_tag_info.value, log_job_events)

    @staticmethod
    def get_processor(type):

        if type == 'FTP':
            return FTPProcessor()
        elif type == 'S3':
            return S3Processor()
        elif type == 'SFTP':
            return SFTPProcessor()
        else:
            raise Exception("ftp data source not supported")
