# -*- coding: utf-8 -*-
__author__ = 'carl'

import os

from db.myredis.redis_cli import RedisClient

'''
基于redis实现分布式锁
实现互斥锁，支持重入和续锁
具体用法参考：test.test_redis_lock
'''
import threading
import weakref

LOCK_SCRIPT = b"""
if (redis.call('exists', KEYS[1]) == 0) then
    redis.call('hincrby', KEYS[1], ARGV[2], 1);
    redis.call('expire', KEYS[1], ARGV[1]);
    return 1;
end ;
if (redis.call('hexists', KEYS[1], ARGV[2]) == 1) then
    redis.call('hincrby', KEYS[1], ARGV[2], 1);
    redis.call('expire', KEYS[1], ARGV[1]);
    return 1;
end ;
return 0;
"""
UNLOCK_SCRIPT = b"""
if (redis.call('hexists', KEYS[1], ARGV[1]) == 0) then
    return nil;
end ;
local counter = redis.call('hincrby', KEYS[1], ARGV[1], -1);
if (counter > 0) then
    return 0;
else
    redis.call('del', KEYS[1]);
    return 1;
end ;
return nil;
"""
RENEW_SCRIPT = b"""
if redis.call("exists", KEYS[1]) == 0 then
    return 1
elseif redis.call("ttl", KEYS[1]) < 0 then
    return 2
else
    redis.call("expire", KEYS[1], ARGV[1])
    return 0
end
"""


class RedisLock(object):
    redis_client = RedisClient().get_redis_cli()

    def __init__(self, lock_name, uid=str(os.getpid()), expire=30, is_renew=True):
        self.conn = RedisLock.redis_client
        self.lock_script = None
        self.unlock_script = None
        self.renew_script = None
        self._register_script()

        self._name = f"lock:{lock_name}"
        self._expire = int(expire)
        self._uid = uid

        self._lock_renew_interval = self._expire * 2 / 3
        self._lock_renew_threading = None

        self.is_renew = is_renew
        self.is_acquired = None
        self.is_released = None

    @property
    def id(self):
        return self._uid

    @property
    def expire(self):
        return self._expire

    def _acquire(self):
        result = self.lock_script(keys=(self._name,), args=(self._expire, self._uid))
        if self.is_renew:
            self._start_renew_threading()
        self.is_acquired = True if result else False
        # print(f"争抢锁：{self._uid} - {self.is_acquired}\n")
        return self.is_acquired

    def _release(self):
        if self.is_renew:
            self._stop_renew_threading()

        result = self.unlock_script(keys=(self._name,), args=(self._uid,))
        self.is_released = True if result else False
        # print(f"{self._uid} 释放锁 {self.is_released}")
        return self.is_released

    def _register_script(self):
        self.lock_script = self.conn.register_script(LOCK_SCRIPT)
        self.unlock_script = self.conn.register_script(UNLOCK_SCRIPT)
        self.renew_script = self.conn.register_script(RENEW_SCRIPT)

    def renew(self, renew_expire=30):
        """续锁时长"""
        result = self.renew_script(keys=(self._name,), args=(renew_expire,))
        if result == 1:
            raise Exception(f"{self._name} 没有获得锁或锁过期！")
        elif result == 2:
            raise Exception(f"{self._name} 未设置过期时间")
        elif result:
            raise Exception(f"未知错误码: {result}")
        # print("成功续锁时长：", renew_expire, "s")

    @staticmethod
    def _renew_scheduler(weak_self, interval, lock_event):
        while not lock_event.wait(timeout=interval):
            lock = weak_self()
            if lock is None:
                break
            lock.renew(renew_expire=lock.expire)
            del lock

    def _start_renew_threading(self):
        self.lock_event = threading.Event()
        self._lock_renew_threading = threading.Thread(target=self._renew_scheduler,
                                                      kwargs={
                                                          "weak_self": weakref.ref(self),
                                                          "interval": self._lock_renew_interval,
                                                          "lock_event": self.lock_event
                                                      })

        self._lock_renew_threading.demon = True
        self._lock_renew_threading.start()

    def _stop_renew_threading(self):
        if self._lock_renew_threading is None or not self._lock_renew_threading.is_alive():
            return
        self.lock_event.set()
        # join 作用是确保thread子线程执行完毕后才能执行下一个线程
        self._lock_renew_threading.join()
        self._lock_renew_threading = None

    def __enter__(self):
        self._acquire()
        return self

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        self._release()

    def lock(self) -> bool:
        """
        加锁
        """
        return self._acquire()

    def unlock(self) -> bool:
        """
        解锁
        return: True / False
        """
        return self._release()
