from ast import literal_eval
import redis
import time

__all__ = ['EasyCelery']

class EasyCelery():
    def __init__(self,
                 host='localhost',
                 password=None,
                 default_celery_keyname='celery',
                 db=0,
                 port=6379,
                 decode_responses=True,
                 **kwargs
                 ):
        self.redis_conn = redis.StrictRedis(
            db=db,
            host=host,
            port=port,
            password=password,
            decode_responses=decode_responses,
            **kwargs,
        )

        self.default_celery_keyname = default_celery_keyname

    def put(self,data,block=True,celery_keyname=None):
        celery_keyname = celery_keyname or self.default_celery_keyname
        def block_llen(self=self):
            while True:
                if self.redis_conn.llen(celery_keyname):
                    time.sleep(1)
                    continue
                return True

        if block:
            block_llen()
        self.redis_conn.rpush(self.default_celery_keyname,str(data))
        return True

    def get(self,block=True,celery_keyname=None):
        celery_keyname = celery_keyname or self.default_celery_keyname
        if block:
            data_str = self.redis_conn.blpop(keys=celery_keyname,timeout=None)[1]

        else:
            data_str = self.redis_conn.lpop(name=celery_keyname)
        return literal_eval(data_str) if data_str != None else None


if __name__ == '__main__':
    ec = EasyCelery()
    ec.put(data={'job':'xxx'})
    print(ec.get())
