# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging.config
import os

from apscheduler.schedulers.gevent import GeventScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from db.myredis.redis_lock import RedisLock
from entity.singleton import Singleton
from util.sys_util import get_mac_address

log = logging.getLogger("log_schedtask")
log_err = logging.getLogger("log_err")
"""
定时任务
1- 基础数据定时更新
2- 选股策略每日执行，更新股票池

usage to see:
app/test/apscheduler_testt.py
https://apscheduler.readthedocs.io/en/3.x/
https://blog.csdn.net/sxdgy_/article/details/126377513
使用 GeventScheduler或者BackgroundScheduler
"""


# TODO
class IAOSTask(Singleton):

    def __init__(self):
        # 本进程标志
        self.uid = get_mac_address() + str(os.getpid())
        # 分布式锁
        self.rl = RedisLock(lock_name="IAOSTask", uid=self.uid, expire=300)
        # 任务调度
        self.scheduler = BackgroundScheduler(timezone='Asia/Shanghai')
