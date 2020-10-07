import os
import dill
import fnmatch

from datetime import datetime


class KVRocket:
    """
    KVRocket is a lightweight persistent key value store for Python.
    """

    def __init__(self, storepath):
        self.storepath = storepath
        if os.path.isfile(storepath):
            self.__load()
        else:
            self.__save(create=True)
            self.__load()

    def __load(self):
        # todo: verify that file is valid "Store" obj.
        self.keys = []
        f = open(self.storepath, "rb")
        self.store = dill.load(f)
        for i in self.store.__dict__:
            if not i.startswith("_"):
                self.keys.append(i)
        f.close()

    def __save(self, create=False):
        f = open(self.storepath, "wb+")
        if create:
            self.store = Store()
            self.store.__created_at = datetime.now()
        self.store.__updated_at = datetime.now()
        dill.dump(self.store, f)
        f.close()

    def get(self, key):
        """ get the value of a given key """
        return getattr(self.store, key)
    
    def get_batch(self, keys):
        results = {}
        for i in keys:
            v = getattr(self.store, i)
            results[i] = v
        return results

    def put(self, key, value):
        """ set the value of a key """
        setattr(self.store, key, value)
        self.__save()
    
    def put_batch(self, kv_pairs):
        """ set the value of a batch of keys """
        for i in kv_pairs:
            setattr(self.store, i, kv_pairs[i])
        self.__save()

    def rem(self, key):
        """ remove the value of a key """
        delattr(self.store, key)
        self.__save()

    def rem_batch(self, items):
        for i in items:
            delattr(self.store, i)
        self.__save()

    def scan(self, prefix):
        """ scan keys. Return keys that match the prefix. """
        matches = []
        for key in self.keys:
            if fnmatch.fnmatch(key, prefix):
                matches.append(key)
        return matches


class Store:
    """ A Store provides the primary storage mechanics for kvrocket. """

    def __init__(self):
        self.__created_at = None
        self.__updated_at = None