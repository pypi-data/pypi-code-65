"""Util module"""
import os
import datetime
from ftplib import FTP
from fluent import event
import pysftp


class FTPUtility:
    """Common methods"""

    @staticmethod
    def log_event(tag, data_dict):
        """ fluentd event generator """
        data_dict['event_datetime'] = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        event.Event(tag, data_dict)

    @staticmethod
    def delete_file(file):
        try:
            os.remove(file)
        except:
            pass

    @staticmethod
    def get_ftp_connection(host, user, password):
        hostport = host.split(":")
        host = hostport[0]
        port = int(hostport[1]) if len(hostport) == 2 else 21
        ftp = FTP(host=host, port=port)
        ftp.login(user, password)
        return ftp

    @staticmethod
    def get_sftp_connection(host, user, password):
        hostport = host.split(":")
        host = hostport[0]
        port = int(hostport[1]) if len(hostport) == 2 else 20
        cinfo = {'host': host, 'username': user, 'password': password,
                 'port': port}
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        sftp = pysftp.Connection(**cinfo, cnopts=cnopts)
        return sftp

