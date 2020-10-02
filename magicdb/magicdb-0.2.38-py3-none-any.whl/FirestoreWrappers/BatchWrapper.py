from magicdb.database import db
from magicdb.utils.Serverless.span import safe_span
import threading


class BatchWrapper:
    def __init__(self, *args, **kwargs):
        self._batch = db.conn.batch(*args, **kwargs)

    def commit(self, *args, **kwargs):
        with safe_span("batch_commit"):
            return self._batch.commit(*args, **kwargs)

    def commit_async(self, *args, **kwargs):
        t = threading.Thread(target=self.commit, args=args, kwargs=kwargs)
        t.start()
        return t

    def set(self, *args, **kwargs):
        return self._batch.set(*args, **kwargs)

    def update(self, *args, **kwargs):
        return self._batch.update(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._batch.delete(*args, **kwargs)
