# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging.config

from apscheduler.schedulers.gevent import GeventScheduler

from entity.singleton import Singleton

log = logging.getLogger("log_schedtask")
log_err = logging.getLogger("log_err")
"""
定时任务  TODO
to see https://apscheduler.readthedocs.io/en/3.x/
使用 GeventScheduler或者BackgroundScheduler
"""


#  TODO
class UpdateDataTask(Singleton):
    pass
