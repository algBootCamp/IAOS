# -*- coding: utf-8 -*-
__author__ = 'carl'

import akshare as ak
from pandas import DataFrame

from util.decorator_util import retry

"""
akshare 数据
to see https://www.akshare.xyz/tutorial.html
"""


@retry(max_retry=5, time_interval=3)
def get_stock_board_industry_summary_ths() -> DataFrame:
    """单次返回当前时刻同花顺行业一览表"""
    df = ak.stock_board_industry_summary_ths()
    return df


@retry(max_retry=5, time_interval=3)
def get_stock_board_industry_name_ths() -> DataFrame:
    """查看同花顺的所有行业名称"""
    df = ak.stock_board_industry_name_ths()
    return df


@retry(max_retry=5, time_interval=3)
def get_stock_board_industry_cons_ths(symbol: str) -> DataFrame:
    """
    单次返回当前时刻 同花顺-板块-行业板块-成份股数据
    symbol	str	行业板块
    可以通过调用 ak.stock_board_industry_name_ths() 查看同花顺的所有行业名称
    """
    df = ak.stock_board_industry_cons_ths(symbol=symbol)
    return df
