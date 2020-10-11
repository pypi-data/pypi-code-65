
import logging

from .defaults import *
from .helpers import Helpers

class Sandbox(object):
    def __init__(self, session):
        self.session = session
    def _do_get_sanbox_report_md5(self, md5hash, report_type):
        path = 'sandbox/report/' + str(md5hash)
        if report_type == 'FULL':
            path += '?details=full'
        else:
            path += '?details=summary'
        res = self.get(path)
        if 'Retry-After' in res:
            LOGGER.error("Zscaler RATE LIMIT REACHED")
            return None
        else:
            return res
    def get_sanbox_report_md5(self, md5hash):
        res = self._do_get_sanbox_report_md5(md5hash, 'FULL')
        return res
    def get_sanbox_report_md5_summary(self, md5hash):
        res = self._do_get_sanbox_report_md5(md5hash, 'SUMMARY')
        return res
    def get_sanbox_report_sha1(self):
        raise NotImplementedError()
    def get_sanbox_report_sha256(self):
        raise NotImplementedError()
    def is_md5hash_suspicious(self, report):
        extrated = (Helpers.extract_values(report, 'Type'))
        if 'SUSPICIOUS' in extrated:
            return True
        else:
            return False
    def is_md5hash_malicious(self, report):
        extrated = (Helpers.extract_values(report, 'Type'))
        if 'MALICIOUS' in extrated:
            return True
        else:
            return False


LOGGER = logging.getLogger(__name__)
