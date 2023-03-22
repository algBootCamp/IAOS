# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging

from db.myredis.redis_cli import RedisClient
from quantization.securitypick.condition.conditionstockpick01 import ConditonStockPick01
# ----  log ------ #
from quantization.securitypick.growth.growthstockpick01 import GrowthStockPick01
from quotation.cache.cache import LocalBasicDataCache

log = logging.getLogger("log_blueprint")
log_err = logging.getLogger("log_err")


# ----  log ------ #


def get_stks_by_cons(condtions_dict) -> dict:
    """
    根据条件选股，返回符合条件的股票
    """
    csp01 = ConditonStockPick01()
    data = csp01.get_target_stock_pool(**condtions_dict)
    if data is None or len(data.index) == 0:
        return "There are no eligible stocks!"
    target_data = {}
    for index, row in data.iterrows():
        symbol = row['symbol']
        target_data[symbol] = row.to_dict()
    return target_data


def get_growthstockpick01_stks(top_num: int, weights: dict) -> dict:
    """获取GrowthStockPick01模型的股票池"""
    if LocalBasicDataCache.base_stock_infos is None:
        rediscli = __getrediscli()
        res = rediscli.get("base_stock_infos")
        if res is None:
            LocalBasicDataCache.load_base_stock_infos()
    # 默认：weights={'roe': 34, 'basic_eps_yoy': 33, 'pe_ttm': 33}
    #      top_num=5
    gsp01 = GrowthStockPick01()
    gsp01.init_data(stocksinfos=LocalBasicDataCache.base_stock_infos, weights=weights)
    stock_pool = {}
    for index, row in gsp01.get_target_stock_pool(top_num=top_num).iterrows():
        symbol = row['symbol']
        stock_pool[symbol] = row.to_dict()
    return stock_pool


def __getrediscli():
    return RedisClient().get_redis_cli()
