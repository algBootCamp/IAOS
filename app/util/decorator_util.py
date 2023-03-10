# # -*- coding: utf-8 -*-
__author__ = 'carl'

import asyncio
import time
from functools import wraps


def retry(max_retry: int = 3, time_interval: int = 1):
    """
    任务重试装饰器:支持异步、同步函数
    max_retry: 最大重试次数 默认3次
    time_interval: 每次重试间隔 默认1s
    """
    def _retry(func):
        # noinspection PyBroadException
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # 同步函数循环重试
            for _ in range(max_retry):
                try:
                    res = func(*args, **kwargs)
                except:
                    time.sleep(time_interval)
                else:
                    return res

        # noinspection PyBroadException
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # 异步循环重试
            for retry_count in range(max_retry):
                try:
                    return await func(*args, **kwargs)
                except:
                    await asyncio.sleep(time_interval)

        wrapper = async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return wrapper

    return _retry
