# -*- coding: utf-8 -*-
# @Time    : 2019-05-29 10:35
# @E-Mail  : wujifan1106@gmail.com
# @Site    : 
# @File    : bloomfilter.py
# @Software: PyCharm
import math
import traceback
from typing import AnyStr

from CBloomfilter import CBloomfilter


class LocalBloomFilter():

    def __init__(self, capacity, error, prime_length=True):
        self.bf = CBloomfilter(capacity, error, prime_length)
        self.bitmap = bytes(int(self.bf.bits / 8) + 1)

    def add(self, data):
        if isinstance(data, (list, tuple)):
            for v in data:
                assert isinstance(v, str), 'add() arg must be a str or list/tuple of strings'
                self.bf.add(self.bitmap, v)
        else:
            assert isinstance(data, str), 'add() arg must be a str or list/tuple of strings'
            self.bf.add(self.bitmap, data)

    def is_contain(self, data):
        if isinstance(data, (list, tuple)):
            for v in data:
                assert isinstance(v, str), 'is_contain() arg must be a str or list/tuple of strings'
            return [self.bf.is_contain(self.bitmap, v) for v in data]
        else:
            assert isinstance(data, str), 'is_contain() arg must be a str or list/tuple of strings'
            return self.bf.is_contain(self.bitmap, data)

    def clean(self):
        self.bf.clean_bitmap(self.bitmap)


class RedisBloomFilter():
    def __init__(self, capacity, error, redis_conn, prime_length=True, filter_prefix="BloomFilter"):
        self.bf = CBloomfilter(capacity, error, prime_length)
        self.total_memory_by_mb = math.ceil(self.bf.bits / 8 / 1024 / 1024)
        self.mem_block_counts = math.ceil(self.total_memory_by_mb / 512)
        self.filter_prefix = filter_prefix
        self.redis_conn = redis_conn
        self.max_offset = 2 ** 32 - 1

    def _add(self, data: AnyStr):
        assert isinstance(data, str), 'add() arg must be a str or list/tuple of strings'
        offset = self.bf.hash(data)
        with self.redis_conn.pipeline() as pipe:
            for o in offset:
                block_num, offset = self._cal_block_index_and_offset(o)
                pipe.setbit(f"{self.filter_prefix}_{block_num}", offset, 1)
            pipe.execute()

    # def _cal_data_block(self, data: AnyStr):
    #     return str(ord(data[0]) % self.mem_block_counts)

    def _cal_block_index_and_offset(self, hash: int):
        return hash // self.max_offset, hash % self.max_offset

    def add(self, data):
        if isinstance(data, (list, tuple)):
            for v in data:
                self._add(v)
        else:
            self._add(data)

    def is_contain(self, data):
        try:
            assert isinstance(data, str), 'is_contain() arg must be a str'
            offset = self.bf.hash(data)
            with self.redis_conn.pipeline() as pipe:
                for o in offset:
                    block_num, offset = self._cal_block_index_and_offset(o)
                    pipe.getbit(f"{self.filter_prefix}_{block_num}", offset)
                results = pipe.execute()
                if sum(results) == self.bf.hashes:
                    return True
                return False
        except Exception:
            print(traceback.format_exc())
            return None

    def clean(self):
        for i in range(self.mem_block_counts):
            self.redis_conn.delete(f"{self.filter_prefix}_{i}")


if __name__ == '__main__':
    f = RedisBloomFilter(100000000, 0.0001, None, True, "test")
    f.add("abc")
