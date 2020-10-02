import magicdb
from magicdb.database import db
from magicdb.utils.Serverless.span import safe_span
import threading
from pydantic import BaseModel
from enum import Enum
from typing import List, Dict, Tuple, Any

# TODO add support for over 500 queries...

MAX_BATCH_SIZE = 500


class OperationType(str, Enum):
    SET = "set"
    UPDATE = "update"
    DELETE = "delete"


class BatchCommand(BaseModel):
    operation_type: OperationType
    args: tuple = ()
    kwargs: dict = {}

    # class Config:
    #     arbitrary_types_allowed = True


class BatchWrapper:
    # init_args: tuple = ()
    # init_kwargs: dict = {}
    # batch_commands: List[BatchCommand] = []
    # batches: List[magicdb.WriteBatch]

    # class Config:
    #     arbitrary_types_allowed = True

    def __init__(self, *args, **kwargs):
        self._init_args: tuple = args
        self._init_kwargs: dict = kwargs
        # self._batch = db.conn.batch(*args, **kwargs)
        self._batch_commands: List[BatchCommand] = []
        # self._batches: List[magicdb.WriteBatch] = []

    def set(self, *args, **kwargs):
        self._batch_commands.append(
            BatchCommand(operation_type=OperationType.SET, args=args, kwargs=kwargs)
        )
        # return self._batch.set(*args, **kwargs)

    def update(self, *args, **kwargs):
        self._batch_commands.append(
            BatchCommand(operation_type=OperationType.UPDATE, args=args, kwargs=kwargs)
        )
        # return self._batch.update(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self._batch_commands.append(
            BatchCommand(operation_type=OperationType.DELETE, args=args, kwargs=kwargs)
        )
        # return self._batch.delete(*args, **kwargs)

    @staticmethod
    def commit_batch(batch, i=None):
        with safe_span("batch_commit"):
            batch.commit()
            print(f"Batch number {i or '?'} committed!")

    def commit_batch_async(self, batch, i=None):
        t = threading.Thread(target=self.commit_batch, args=(batch, i))
        t.start()
        return t

    def commit_batches(self, batches: List[magicdb.WriteBatch], sync=False):
        if not sync:
            ts = [self.commit_batch_async(batch, i) for i, batch in enumerate(batches)]
            [t.join() for t in ts]
        else:
            [self.commit_batch(batch, i) for i, batch in enumerate(batches)]

    def commit(self, sync=False):
        batches: List[magicdb.WriteBatch] = self.make_batches()
        self.commit_batches(batches=batches, sync=sync)

    def commit_async(self, *args, **kwargs):
        t = threading.Thread(target=self.commit, args=args, kwargs=kwargs)
        t.start()
        return t

    def make_batches(self) -> List[magicdb.WriteBatch]:
        chunks = self.chunk_array(arr=self._batch_commands, chunk_size=MAX_BATCH_SIZE)
        batches: List[magicdb.WriteBatch] = []
        for i, chunk in enumerate(chunks):
            batch: magicdb.WriteBatch = db.conn.batch(
                *self._init_args, **self._init_kwargs
            )
            for batch_command in chunk:
                batch_command: BatchCommand
                if batch_command.operation_type == OperationType.SET:
                    batch.set(*batch_command.args, **batch_command.kwargs)
                elif batch_command.operation_type == OperationType.UPDATE:
                    batch.update(*batch_command.args, **batch_command.kwargs)
                elif batch_command.operation_type == OperationType.DELETE:
                    batch.delete(*batch_command.args, **batch_command.kwargs)

            batches.append(batch)
            print(f"Batch number {i} added")
        return batches

    @staticmethod
    def chunk_array(arr, chunk_size):
        return [arr[i : i + chunk_size] for i in range(0, len(arr), chunk_size)]
