import time
from aioredlock.errors import LockError
import asyncio


async def redis_get_lock_with_timeout(lock_manager, resource, timeout=30, lock_timeout=None, sleep_second=0.1):
    """
    获取锁

    Args:

        lock_manager (Aioredlock): aioredlock的lock_manager

        resource (str): name

        timeout (int): 单位/s, 获取锁的超时时间

        lock_timeout int(s): 单位/s, 锁的持有时间

        sleep_second  (float): 获取失败之后的睡眠时间
    """
    now = int(time.time())
    end = now + timeout
    while 1:
        try:
            lock = await lock_manager.lock(resource,
                                           lock_timeout=lock_timeout)
            return lock
        except LockError:
            now = int(time.time())
            if now >= end:
                raise
            await asyncio.sleep(sleep_second)
