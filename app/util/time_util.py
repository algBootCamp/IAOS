# -*- coding: utf-8 -*-
__author__ = 'carl'

import time


def get_today_Ymd() -> str:
    """获取 本日 YYYYMMDD """
    today_str = time.strftime("%Y%m%d", time.localtime())
    return today_str


def get_befortoday_Ymd(n: int) -> str:
    """获取 本日前n日 YYYYMMDD """
    # python时间戳 时间间隔是以秒为单位的浮点小数
    today_ticks = time.time()
    div_ticks = n * 24 * 60 * 60
    tartget_ticks = today_ticks - div_ticks
    tartget_day_str = time.strftime("%Y%m%d", time.localtime(tartget_ticks))
    return tartget_day_str


def get_after_today_Ymd(n: int) -> str:
    """获取 本日后n日 YYYYMMDD """
    return get_befortoday_Ymd(-n)
