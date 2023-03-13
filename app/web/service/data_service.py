# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging
import threading

from db.myredis.redis_cli import RedisClient
from quotation.cache.cache import LocalBasicDataCache, RemoteBasicDataCache
from util.obj_util import loads_data

# ----  log ------ #
log = logging.getLogger("log_blueprint")
log_err = logging.getLogger("log_err")


# ----  log ------ #

def to_refresh_cache():
    """强制刷新缓存"""
    log.info("refresh the remote & local cache.")

    def refresh():
        # TODO
        """常用基础数据缓存"""
        from quotation.cache.cache import RemoteBasicDataCache, LocalBasicDataCache
        RemoteBasicDataCache.refresh(is_request=True)
        # 保证RemoteBasicDataCache.refresh执行结束，再进行LocalBasicDataCache.refresh
        LocalBasicDataCache.refresh()

    t1 = threading.Thread(target=refresh)
    t1.start()

def get_industry():
    """
    获取行业信息
    """
    if LocalBasicDataCache.industry_set is not None:
        return LocalBasicDataCache.industry_set
    else:
        rediscli = __getrediscli()
        res = rediscli.get("industry_set")
        if res is None:
            LocalBasicDataCache.load_smb_industry_map()
            res = rediscli.get("industry_set")
        return loads_data(res)


def __getrediscli():
    return RedisClient().get_redis_cli()
