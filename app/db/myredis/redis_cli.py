# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging

import redis
from redis import StrictRedis

from conf.globalcfg import GlobalCfg

"""
redis client
内部自有连接池  [使用使用阻塞连接池：当连接池中没有空闲的连接时，会等待timeout秒，直到获取到连接或超时报错。]
使用时世界获取连接  进行操作即可
"""
log = logging.getLogger("app")
log_err = logging.getLogger("log_err")


# noinspection PyBroadException
class RedisClient(object):
    __pool = None
    global_cfg = GlobalCfg()
    redis_info = global_cfg.get_redis_info()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'inst'):
            cls.inst = super(RedisClient, cls).__new__(cls, *args, **kwargs)
        return cls.inst

    def __init__(self):
        if self.__pool is None:
            try:
                self.__pool = redis.BlockingConnectionPool(host=self.redis_info['host'],
                                                           port=int(self.redis_info['port']),
                                                           db=int(self.redis_info['db']),
                                                           max_connections=int(self.redis_info['max_connections']),
                                                           timeout=int(self.redis_info['timeout']))
                log.info("redis pool init success.")
            except Exception as e:
                log_err.error("redis pool init failed.%s" % e)

    def get_redis_cli(self) -> StrictRedis:
        try:
            redis_conn = StrictRedis(connection_pool=self.__pool)
            if redis_conn.ping():
                return redis_conn
        except Exception as e:
            log_err.error("can't obtain a redis connection.%s" % e)
            return None
