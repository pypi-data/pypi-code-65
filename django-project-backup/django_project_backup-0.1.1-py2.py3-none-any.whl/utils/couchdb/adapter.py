from cloudant import CouchDB
from cloudant.error import CloudantDatabaseException

from ...settings import COUCHDB_DATASTORE_USER, COUCHDB_DATASTORE_PASSWORD, COUCHDB_DATASTORE_HOST, \
                        COUCHDB_DATASTORE_DATABASE_NAME


class DBAdapter:
    """
    CouchDB DBAdapter
    """
    def __init__(self):
        self.client = CouchDB(COUCHDB_DATASTORE_USER, COUCHDB_DATASTORE_PASSWORD,
                              url=COUCHDB_DATASTORE_HOST,
                              connect=True,
                              auto_renew=True,
                              use_basic_auth=True)

        try:
            self.database = self.client[COUCHDB_DATASTORE_DATABASE_NAME]
        except KeyError:
            self.database = self.client.create_database(COUCHDB_DATASTORE_DATABASE_NAME)

    def __del__(self):
        self.client.disconnect()

    def put_documents(self, docs):
        return self.database.bulk_docs(docs)
        # cloudant should return [{'ok': True, 'id': '1', 'rev': 'n-xxxxxxx'}]

    def put_document(self, doc):
        try:
            _res = self.database.create_document(doc, throw_on_exists=True)
            return True

        except CloudantDatabaseException:
            updated = False

            while not updated:
                existing = self.database.all_docs(key=doc['_id'])['rows'][0]
                # cloudant should return {'id': '1', 'key': '1', 'value': {'rev': 'n-xxxxxxx'}}

                existing_rev = existing['value']['rev']
                doc['_rev'] = existing_rev

                _updated = self.put_documents([doc])
                updated = len(list(filter(lambda x: x['ok'], filter(lambda x: x['id'] == doc['_id'], _updated)))) == 1

            return updated

    def get_documents(self):
        return self.database.all_docs(include_docs=True)
