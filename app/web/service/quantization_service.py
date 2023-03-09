# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging

from db.myredis.redis_cli import RedisClient
from quantization.securitypick.conditionstockpick01 import ConditonStockPick01

# ----  log ------ #
log = logging.getLogger("log_blueprint")
log_err = logging.getLogger("log_err")


# ----  log ------ #


def get_stks_by_cons(condtions_dict) -> dict:
    """
    根据条件选股，返回符合条件的股票
    """
    csp01 = ConditonStockPick01()
    data = csp01.get_target_data(**condtions_dict)
    if data is None or len(data.index) == 0:
        return "There are no eligible stocks!"
    target_data = {}
    for index, row in data.iterrows():
        symbol = row['symbol']
        target_data[symbol] = row.to_dict()
    return target_data


def __getrediscli():
    return RedisClient().get_redis_cli()
