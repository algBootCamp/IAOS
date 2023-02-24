# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging

from dbutils.pooled_db import PooledDB
from conf.globalcfg import GlobalCfg

"""
功能：创建数据库连接池
"""
log = logging.getLogger("app")
log_err = logging.getLogger("log_err")


# noinspection PyBroadException
class MyConnectionPool(object):
    __pool = None
    global_cfg = GlobalCfg()
    db_info = global_cfg.get_db_info()

    def __enter__(self):
        """创建数据库连接conn和游标cursor"""
        self.conn = self.__getconn()
        self.cursor = self.conn.cursor()

    def __getconn(self):
        """创建数据库连接池"""
        if self.__pool is None:
            try:
                self.__pool = PooledDB(
                    creator=self.db_info["creator"],
                    mincached=self.db_info["mincached"],
                    maxcached=self.db_info["maxcached"],
                    maxshared=self.db_info["maxshared"],
                    maxconnections=self.db_info["maxconnections"],
                    blocking=self.db_info["blocking"],
                    maxusage=self.db_info["maxusage"],
                    setsession=self.db_info["setsession"],
                    host=self.db_info["host"],
                    port=self.db_info["port"],
                    user=self.db_info["user"],
                    passwd=self.db_info["passwd"],
                    db=self.db_info["db"],
                    use_unicode=False,
                    charset=self.db_info["charset"],
                )
            except Exception as e:
                log_err.error("create mysql ConnectionPool failed.", e)
                return None
        log.info("create mysql ConnectionPool success.")
        return self.__pool.connection()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """释放连接池资源"""
        self.cursor.close()
        self.conn.close()

    def getconn(self):
        """从连接池中取出一个连接"""
        try:
            conn = self.__getconn()
            cursor = conn.cursor()
            return cursor, conn
        except Exception as e:
            log_err.error("get conn from mysql ConnectionPool failed.", e)
            return None, None
