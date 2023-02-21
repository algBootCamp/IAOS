# -*- coding: utf-8 -*-
__author__ = 'carl'

import functools
import logging
from flask import Blueprint, request, render_template, session, Response, redirect
# noinspection SpellCheckingInspection
from controller.entity.jsonresp import JsonResponse
from quantization.securitypick.stockpick01 import StockPick01


# --------- blueprint util --------- #
def blueprintlog(lg):
    """log blueprint decorator"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            lg.info("访问 %s 接口." % func.__name__)
            return func(*args, **kw)
        return wrapper
    return decorator
# --------- blueprint util --------- #


# ----  log ------ #
log = logging.getLogger("log_blueprint")
log_err = logging.getLogger("log_err")
# ----  log ------ #

# contoller
blue = Blueprint('blue', __name__)

'''
进行大小盘分类、行业分类，基于此根据股票财务和行情指标进行排序，通过设置参数和过滤值筛选股票。
具体指标包括 动态市盈率、市净率、流通股本、总市值、每股公积金、每股收益、收入同比、利润同比、毛利率、净利润率等。
'''
stkp01: StockPick01 = StockPick01()


# main
@blue.route('/', methods=['POST', 'GET'])
@blueprintlog(log)
def main():
    # log.info("访问 %s 接口." % sys._getframe().f_code.co_name)
    return 'Hello IAOS Server ~ '


@blue.route('/display_industry.do', methods=['POST', 'GET'])
@blueprintlog(log)
def display_industry():
    """
    展示行业分类
    """
    # log.info("访问 %s 接口." % sys._getframe().f_code.co_name)
    return list(StockPick01.industry_set)


@blue.errorhandler(Exception)
def error_handler(e):
    """
    全局异常捕获，也相当于一个视图函数
    """
    log_err.error("接口访问异常!", e)
    return JsonResponse.error(msg=str(e))



