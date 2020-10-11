import datetime
import logging
import json

from .defaults import *

class AdminAuditLogs(object):
    def __init__(self, session):
        self.session = session
    def get_auditlog_entry_report(self):
        path = 'auditlogEntryReport'
        # status complete
        # download
        return self.session.get(path)
    def generate_auditlog_entry_report(self, start, end, page, page_size):
        # start : startdatetime
        # end : enddatetime
        path = 'auditlogEntryReport'
        body = {
            # epoch in millisec
            'startTime': int(start.timestamp()*1000),
            'endTime': int(end.timestamp()*1000),
            'page': page,
            'pageSize': page_size
        }
        return self.session.post(path, body)
    def wait_for_completion(self, timeout=600):
        status = {'status':'not started yet'}
        s = datetime.datetime.now()
        while status['status'] != 'COMPLETE':
            status = self.get_auditlog_entry_report()
            e = datetime.datetime.now()
            if (e - s).seconds > timeout:
                raise RuntimeError('timeout')
        return status
    def download_auditlog_entry_report(self):
        # timezone が PDT になってる
        self.wait_for_completion()
        path = 'auditlogEntryReport/download'
        return self.session.get(path)

LOGGER = logging.getLogger(__name__)
