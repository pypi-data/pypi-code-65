'''
This module manages the config for the service.
'''
import logging
import uuid

from sql30 import db


log = logging.getLogger(__name__)

class ConfigManager(db.Model):
    TABLE = 'config'
    PKEY = 'cid'
    DB_SCHEMA = {
        'db_name': 'reviews.db',
        'tables': [
            {
                'name': TABLE,
                'fields': {
                    'cid': 'uuid',
                    'key': 'text',
                    'value': 'text',
                    'desc': 'text',
                    'scope': 'text'
                    },
                'primary_key': PKEY
            }]
        }
    VALIDATE_BEFORE_WRITE = True

    SCOPE = ['LOCAL', 'GLOBAL']

    def __init__(self):
        super(ConfigManager, self).__init__()
        self._cache = {}

    def get(self, key, record=False):
        if key in self._cache:
            rec = self._cache[key]
            if not record:
                return rec['val']
            else:
                return rec
        return None

    def set(self, key, val, desc=None, scope='LOCAL'):
        rec = {}
        rec['cid'] = '%s' % uuid.uuid4()
        rec['key'] = key
        rec['val'] = val
        rec['desc'] = '%s' % desc

        assert scope in self.SCOPE, "Invalid scope %s" % scope
        rec['scope'] = scope

        try:
            # persist each config so that it can be retrieved in case of 
            # service restart / failure.
            self.write(self.TABLE, **rec) 
            # keep the config in sync with local cache always so that reads
            # do not strain DB and are faster.
            self._cache[key] = rec
        except Exception as err:
            log.error("Unable to set config : %r", rec)
            return None
        return rec  # record with uuid for future reference
