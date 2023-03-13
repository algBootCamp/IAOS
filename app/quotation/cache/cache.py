# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging
import os
import time

from db.myredis.redis_cli import RedisClient
from db.myredis.redis_lock import RedisLock
from quotation.cleaning.data_clean import BaseDataClean
from util.obj_util import dumps_data, loads_data
from util.sys_util import get_mac_address

'''
常用基础数据缓存，每日自动拉取一次，可主动刷新
-- 远程缓存：只有一个进程每日更新
-- 本地缓存：每个进程从远程缓存拉去数据【保证每个进程缓存一致】
'''

# ----  log ------ #
log = logging.getLogger("app")
log_err = logging.getLogger("log_err")


# ----  log ------ #

# noinspection SpellCheckingInspection,PyMethodMayBeStatic
class RemoteBasicDataCache(object):
    instance = None
    # 0:未更新 1：已更新
    updateflag = 0
    rediscli = RedisClient().get_redis_cli()
    # 本进程标志
    uid = get_mac_address() + str(os.getpid())
    # 分布式锁
    rl = RedisLock(lock_name="IAOSTask", uid=uid, expire=30)

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    @classmethod
    def refresh(cls, is_request=False):
        """
        args：is_request=True: 前端请求强制刷新缓存
        """
        res = False
        cls.updateflag = 0
        cls.rediscli.set("RemoteBasicDataCache.updateflag", cls.updateflag)
        try:
            if is_request:
                cls.store_base_stock_infos()
                cls.store_smb_industry_map()
                res = True
                cls.updateflag = 1
                cls.rediscli.set("RemoteBasicDataCache.updateflag", cls.updateflag)
                log.info("远程全部股票每日重要的基础数据更新完毕.")
                return res
            if not is_request and cls.rl.lock():
                cls.store_base_stock_infos()
                cls.store_smb_industry_map()
                res = True
                cls.updateflag = 1
                cls.rediscli.set("RemoteBasicDataCache.updateflag", cls.updateflag)
                log.info("远程全部股票每日重要的基础数据更新完毕.")
        except Exception as e:
            log_err.error("远程全部股票每日重要的基础数据更新失败！%s" % e)
        finally:
            cls.rl.unlock()
        return res

    @classmethod
    def store_base_stock_infos(cls):
        """
        存储下述信息进redis
        ['TS股票代码', '股票代码', '股票名称', '地区', '行业', '市场', '上市日期', '交易所',
         '市盈率', '市盈率TTM', '市净率', '市销率', '市销率TTM', '总股本', '流通股本', '总市值', '流通市值',
         '股息率', '股息率TTM', '涨跌幅', '现价', '成交量', '换手率', '成交额',
         '公告日期', '报告期', '基本每股收益', '流动比率', '速动比率', '每股净资产', '销售净利率',
         '销售毛利率', '净利润率', '营业利润率', '净资产收益率', '总资产报酬率', '总资产净利润', '投入资本回报率',
         '年化净资产收益率','年化总资产报酬率', '资产负债率', '营业利润同比增长率', '利润总额同比增长率',
         '营业总收入同比增长率', '营业收入同比增长率', '净资产同比增长率', '更新标识'
         ]
        """
        base_stock_infos = BaseDataClean.init_base_stock_infos()
        # base_stock_infos.to_csv("/Users/zhangtao/projects/IAOS/iaos-server/app/test/testdata/base_stock_infos.csv")
        BaseDataClean.stocks_pool.to_csv("/Users/zhangtao/projects/IAOS/iaos-server/app/test/testdata/stocks_pool.csv")
        cls.rediscli.set("base_stock_infos", dumps_data(base_stock_infos))
        cls.rediscli.set("stocks_pool", dumps_data(BaseDataClean.stocks_pool))

    @classmethod
    def store_smb_industry_map(cls):
        """
        存储下述数据进redis：
        {
             "小盘股":{"行业1":stockinfoDataFrame,"行业2":stockinfoDataFrame,...},
             "中盘股":{"行业1":stockinfoDataFrame,"行业2":stockinfoDataFrame,...},
             "大盘股":{"行业1":stockinfoDataFrame,"行业2":stockinfoDataFrame,...}
        }
        ["行业1","行业2",... ...]
        """
        smb_industry_map = BaseDataClean.init_smb_industry_map()
        industry_set = BaseDataClean.industry_set
        cls.rediscli.set("smb_industry_map", dumps_data(smb_industry_map))
        cls.rediscli.set("industry_set", dumps_data(industry_set))


# noinspection SpellCheckingInspection,PyMethodMayBeStatic
class LocalBasicDataCache(object):
    instance = None
    rediscli = RedisClient().get_redis_cli()
    smb_industry_map = None
    industry_set = None
    base_stock_infos = None
    stocks_pool = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    @classmethod
    def refresh(cls):
        try:
            while int(cls.rediscli.get("RemoteBasicDataCache.updateflag")) == 0:
                time.sleep(1)
            cls.load_base_stock_infos()
            cls.load_smb_industry_map()
            log.info("本地加载全部股票每日重要的基础数据完毕.")
        except Exception as e:
            log_err.error("本地加载全部股票每日重要的基础数据失败！%s" % e)

    @classmethod
    def load_base_stock_infos(cls):
        """
        加载下述信息
        ['TS股票代码', '股票代码', '股票名称', '地区', '行业', '市场', '上市日期', '交易所',
         '市盈率', '市盈率TTM', '市净率', '市销率', '市销率TTM', '总股本', '流通股本', '总市值', '流通市值',
         '股息率', '股息率TTM', '涨跌幅', '现价', '成交量', '换手率', '成交额',
         '公告日期', '报告期', '基本每股收益', '流动比率', '速动比率', '每股净资产', '销售净利率',
         '销售毛利率', '净利润率', '营业利润率', '净资产收益率', '总资产报酬率', '总资产净利润', '投入资本回报率',
         '年化净资产收益率','年化总资产报酬率', '资产负债率', '营业利润同比增长率', '利润总额同比增长率',
         '营业总收入同比增长率', '营业收入同比增长率', '净资产同比增长率', '更新标识'
         ]
        """
        data = cls.rediscli.get("base_stock_infos")
        data1 = cls.rediscli.get("stocks_pool")
        if data is not None and data1 is not None:
            cls.base_stock_infos = loads_data(data)
            cls.stocks_pool = loads_data(data1)
        else:
            cls.base_stock_infos = BaseDataClean.init_base_stock_infos()
            cls.stocks_pool = BaseDataClean.stocks_pool
            cls.rediscli.set("base_stock_infos", dumps_data(cls.base_stock_infos))
            cls.rediscli.set("stocks_pool", dumps_data(cls.stocks_pool))

    @classmethod
    def load_smb_industry_map(cls):
        """
        加载下述数据：
        {
             "小盘股":{"行业1":stockinfoDataFrame,"行业2":stockinfoDataFrame,...},
             "中盘股":{"行业1":stockinfoDataFrame,"行业2":stockinfoDataFrame,...},
             "大盘股":{"行业1":stockinfoDataFrame,"行业2":stockinfoDataFrame,...}
        }
        ["行业1","行业2",... ...]
        """
        data = cls.rediscli.get("smb_industry_map")
        if data is not None:
            cls.smb_industry_map = loads_data(data)
        else:
            cls.smb_industry_map = BaseDataClean.init_smb_industry_map()
            cls.rediscli.set("smb_industry_map", dumps_data(cls.smb_industry_map))
        data = cls.rediscli.get("industry_set")
        if data is not None:
            cls.industry_set = loads_data(data)
        else:
            cls.industry_set = BaseDataClean.industry_set
            cls.rediscli.set("industry_set", dumps_data(cls.industry_set))
