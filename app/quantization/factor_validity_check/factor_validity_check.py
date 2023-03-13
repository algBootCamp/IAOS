# -*- coding: utf-8 -*-
__author__ = 'carl'

from db.myredis.redis_cli import RedisClient
from entity.singleton import Singleton
from quotation.cache.cache import LocalBasicDataCache
from util.obj_util import loads_data
from util.time_util import get_today_Ymd

"""
针对每个候选因子

0- 获取股票池，取近15年内均有数据的股票，以此为基准
1- 选择最近15年（每年每个月月中的数据）内每个股票数据
2- 每个月中计算每只股票的 因子X ，并排序打分，分为5组
3- 计算因子X在5个分组中的 年化复合收益率、超额收益、收益与分值相关性
"""


class FactorValidityCheck(Singleton):

    def __init__(self, factor='pe_ttm'):
        self.factor = factor
        self.rediscli = RedisClient().get_redis_cli()
        self.basic_stocks = None

    def get_basic_stocks(self):
        """获取15年内均有数据的股票"""
        self.basic_stocks = LocalBasicDataCache.stocks_pool
        if not self.basic_stocks:
            self.basic_stocks = loads_data(self.rediscli.get("stocks_pool"))
        today = int(get_today_Ymd())
        self.basic_stocks = self.basic_stocks[(today - self.basic_stocks["list_date"].astype('int')) > 150000]
        # print(self.basic_stocks)


