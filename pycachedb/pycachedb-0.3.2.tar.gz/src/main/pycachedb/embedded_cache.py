import dbm
import shelve
import pathlib
import ZODB, BTrees.OOBTree, BTrees.IIBTree, BTrees.IOBTree
import redis
import time

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class EmbeddedCache(metaclass=Singleton):
    def __init__(self):
        # print('Which db: ', dbm.whichdb('./cache.db'))
        '''
        db = None
        while(not db):
            db = self.create()
            if not db:
                time.sleep(1)
        connection = db.open()
        root = connection.root
        root.t = BTrees.OOBTree.BTree()
        self.db = root.t
        '''
        # self.db = redis.StrictRedis(host="172.21.15.18", port=6379, db=0, password='mG24+lDZurzPzeMQK9+/2RO91bGG//OvM5GszxP8unu3G9WNUMVMdm01z6xd802PpE9HNR1zUTSbtgd/')
        # self.db.flushdb()
        self.root, self.t = self.connect()

    def create(self):
        try:
            # print('First connect DB')
            db = ZODB.DB(str(pathlib.Path(__file__).parent.absolute())+'/db/cache.fs')
            return db
        # except:
        except Exception as e:
            print('Retry connect DB')
            print(e)
            return None

    def connect(self):
        db = None
        while(not db):
            db = self.create()
            if not db:
                time.sleep(1)
        connection = db.open()
        root = connection.root
        root.t = BTrees.OOBTree.BTree()
        return db, root.t

    def set_filters(self, data):
        # root, t = self.connect()
        self.t['filters'] = data
        self.root.close()

    def get_filters(self):
        filters = None
        # root, t = self.connect()
        filters = self.t.get('filters')
        self.root.close()
        return filters

    def reset_filters(self):
        # root, t = self.connect()
        if self.t.get('filters'):
            del self.t['filters']
        self.root.close()
        

    def insert(self, key, parent=None, data=None):
        if parent:
            key = '.'.join((parent, key))

        # with dbm.open('cache', 'c') as db:
        # with shelve.open(str(pathlib.Path(__file__).parent.absolute())+'/db/log', 'c') as db:
        #     db[key] = data
            # assert db[key.encode('utf-8')] == data.encode('utf-8')
            # assert db[key] == data.encode('utf-8')
        # self.db[key] = data
        self.t[key] = data

    def search(self, key, parent=None):
        if parent:
            key = '.'.join((parent, key))
        
        # with dbm.open('cache', 'r') as db:
        # with shelve.open(str(pathlib.Path(__file__).parent.absolute())+'/db/log', 'r') as db:
        #     return db.get(key, None)
        # return self.db[key]
        return self.t.get(key)

    def keys(self):
        # with dbm.open('cache', 'r') as db:
        # with shelve.open(str(pathlib.Path(__file__).parent.absolute())+'/db/log', 'r') as db:
        #     return db.keys()
        # return self.db.keys()
        return self.t.keys()

    def list_all(self):
        # with dbm.open('cache', 'r') as db:
        # with shelve.open(str(pathlib.Path(__file__).parent.absolute())+'/db/log', 'r') as db:
        #     # print('All keys():', db.keys())
        #     return dict(map(lambda k: (k, db.get(k)), db.keys()))
        # return dict(map(lambda k: (k, self.db.get(k)), self.db.keys()))
        return dict(map(lambda k: (k, self.t.get(k)), self.t.keys()))

    def delete(self, key, parent=None):
        if parent:
            key = '.'.join((parent, key))
        
        # with dbm.open('cache', 'w') as db:
        # with shelve.open(str(pathlib.Path(__file__).parent.absolute())+'/db/log', 'w') as db:
        #     if db.get(key, None):
        #         del db[key]
            # print('Remaining keys():', db.keys())
        # del self.db[key]
        if self.t.get(key):
            del self.t[key]

    def clear(self):
        # with dbm.open('cache', 'w') as db:
        # with shelve.open(str(pathlib.Path(__file__).parent.absolute())+'/db/log', 'w') as db:
        #     db.clear()
                # del db[key]
        # self.db.clear()
        self.t.clear()

