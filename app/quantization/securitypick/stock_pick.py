# -*- coding: utf-8 -*-
__author__ = 'carl'

"""
量化选股、条件选股基类
"""


class StockPick(object):

    def init_data(self, *args, **kws):
        """初始化所需数据或者参数"""
        pass

    def get_target_stock_pool(self, *args, **kws):
        """获取该模型下得到的股票池"""
        pass
