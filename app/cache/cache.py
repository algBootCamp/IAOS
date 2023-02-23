# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging

from pandas import DataFrame

'''
常用基础数据缓存，每日自动拉取一次，可主动刷新
'''
from quotation.captures.tsdata_capturer import TuShareDataCapturer

# ----  log ------ #
log = logging.getLogger("app")
# ----  log ------ #

# noinspection SpellCheckingInspection,PyMethodMayBeStatic
class BasicDataCache(object):
    instance = None
    # 全部股票每日重要的基本面指标
    daily_basic_data = DataFrame()

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self) -> object:
        self.datacapture = TuShareDataCapturer()

    def refresh(self):
        BasicDataCache.daily_basic_data = self.datacapture.get_daily_basic()
        log.info("全部股票每日重要的基本面指标更新完毕.")