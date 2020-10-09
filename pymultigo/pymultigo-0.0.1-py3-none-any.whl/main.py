import random
import pymongo

class MongoClient():
    def __init__(self, *uris):
        self.uris = uris
    
    def __getitem__(self, dbname):
        dbs = []
        for uri in self.uris:
            db = {
                'client': pymongo.MongoClient(uri)[dbname],
                'storage': 480,
            }
            dbs.append(db)
        return MultigoDatabase(dbs)

    def get_default_database(self):
        dbs = []
        for uri in self.uris:
            db = {
                'client': pymongo.MongoClient(uri).get_default_database(),
                'storage': 480,
            }
            dbs.append(db)
        return MultigoDatabase(dbs)

class MultigoDatabase():
    def __init__(self, dbs):
        self.dbs = dbs

    def __getitem__(self, colname):
        cols = []
        for db in self.dbs:
            col = {
                'client': db['client'][colname],
                'nospace': self._total_size(db) >= db['storage']*0.99,
            }
            cols.append(col)
        return MultigoCollection(cols)

    def _stats(self, db):
        return db['client'].command("dbstats")

    def _total_size(self, db):
        return int(self._stats(db)['storageSize']) // (1000*1000)
    
class MultigoCollection():
    def __init__(self, cols):
        self.cols = cols

    def find_one(self, condition):
        for col in self.cols:
            if result := col['client'].find_one(condition):
                return result
        return None

    def find(self, condition=None):
        result = []
        for col in self.cols:
            result.extend(list(col['client'].find(condition)))
        return result
    
    def insert_one(self, document):
        for col in self.cols:
            if not col['nospace']:
                return col['client'].insert_one(document)
        return None

    def insert_many(self, documents):
        result = []
        for document in documents:
            result.append(self.insert_one(document))
        return result

    def insert(self, document):
        if isinstance(document, dict):
            return self.insert_one(document)
        else:
            return self.insert_many(document)

if __name__ == "__main__":
    pass