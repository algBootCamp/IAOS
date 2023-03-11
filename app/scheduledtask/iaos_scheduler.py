# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging.config
import os

# from apscheduler.schedulers.gevent import GeventScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler
from flask_apscheduler import APScheduler

from db.myredis.redis_lock import RedisLock
from entity.singleton import Singleton
from quotation.cache.cache import RemoteBasicDataCache, LocalBasicDataCache
from util.sys_util import get_mac_address

log = logging.getLogger("log_schedtask")
log_err = logging.getLogger("log_err")
"""
定时任务
1- 基础数据定时更新
2- 选股策略每日执行，更新股票池 [每个策略模型一个任务，利用分布式锁尽可能进程间均匀执行]

！注意定时任务的时间间隔：数据缓存在策略前，策略之间的时间间隔保留是尽可能完全执行结束
! trigger: 触发器类型：“date”、“cron”、“interval” 
usage to see:
app/test/apscheduler_testt.py
https://apscheduler.readthedocs.io/en/3.x/
https://blog.csdn.net/sxdgy_/article/details/126377513
使用 GeventScheduler或者BackgroundScheduler
"""


# TODO
# noinspection PyMethodMayBeStatic
class IAOSTask(Singleton):

    def __init__(self, app):
        # 本进程标志
        self.uid = get_mac_address() + str(os.getpid())
        # 分布式锁
        self.rl = RedisLock(lock_name="IAOSTask", uid=self.uid, expire=30)

        # 任务调度 执行器：后续根据实际情况调整 todo
        self.executors = {
            'default': ThreadPoolExecutor(max_workers=4),
            'processorpool': ProcessPoolExecutor(max_workers=2)
        }
        self.job_defaults = {
            'coalesce': True,
            'max_instances': 4,  # 并发运行新job默认最大实例多少
            'misfire_grace_time': None
        }
        # 任务调度
        self.core_scheduler = BackgroundScheduler()
        self.core_scheduler.configure(jobstore='default', executors=self.executors,
                                      job_defaults=self.job_defaults, timezone='Asia/Shanghai')
        self.scheduler = APScheduler(scheduler=self.core_scheduler)
        self.scheduler.init_app(app)

    def __update_remote_base_data(self):
        """
        远程基础数据定时更新
        """
        try:
            log.info("start IAOSTask __update_remote_base_data.")
            RemoteBasicDataCache.refresh()
            log.info("execute IAOSTask __update_remote_base_data success.")
        except Exception as e:
            log_err.error("execute IAOSTask __update_remote_base_data failed. {}".format(e))

    def __update_local_base_data(self):
        """
        本地基础数据定时加载更新
        """
        try:
            log.info("start IAOSTask __update_local_base_data.")
            LocalBasicDataCache.refresh()
            log.info("execute IAOSTask __update_local_base_data success.")
        except Exception as e:
            log_err.error("execute IAOSTask __update_local_base_data failed. {}".format(e))

    def __pick_stock(self):
        """
        todo
        选股策略每日执行，更新股票池
        """
        try:
            if self.rl.lock():
                log.info("start IAOSTask pick_stock.")
                # todo
                log.info("execute IAOSTask pick_stock success.")
        except Exception as e:
            log_err.error("execute IAOSTask pick_stock failed. {}".format(e))
        finally:
            self.rl.unlock()

    def __job_exception_listener(self, event):
        """事件监听"""
        if event.exception:
            log_err.error("The job {} crashed : {}.".format(event, event.exception))
        else:
            pass
            # log.info('The job {} worked .'.format(event))

    def remove_job(self, job_id):
        """删除任务"""
        self.scheduler.remove_job(job_id)
        log.info('The job {} removed.'.format(job_id))

    def pause_job(self, job_id):
        """暂停任务"""
        self.scheduler.pause_job(job_id)
        log.info('The job {} paused.'.format(job_id))

    def resume_job(self, job_id):
        """恢复任务"""
        self.scheduler.resume_job(job_id)
        log.info('The job {} resumed'.format(job_id))

    def get_jobs(self):
        """获取所有job信息"""
        return self.scheduler.get_jobs()

    def start_task(self):
        # 从2023年3月1日开始后的的每天的8点0分执行
        self.scheduler.add_job(id='1', func=self.__update_remote_base_data, trigger='cron', day_of_week='0-6', hour=10,
                               minute=26,
                               start_date='2023-3-1', end_date='2099-3-1')
        # 从2023年3月1日开始后的的每天的8点5分执行
        self.scheduler.add_job(id='2', func=self.__update_local_base_data, trigger='cron', day_of_week='0-6', hour=10,
                               minute=29,
                               start_date='2023-3-1', end_date='2099-3-1')

        # 从2023年3月1日开始后的的每周一到周五的23点23分执行
        # self.scheduler.add_job(id='3', func=self.__pick_stock, 'cron', day_of_week='mon-fri', hour=23, minute=23,
        #                        start_date='2023-3-1')
        # 设置任务监听
        self.scheduler.add_listener(self.__job_exception_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        # 开始执行调度
        self.scheduler.start()
        log.info("IAOSTask scheduler running ... ")
