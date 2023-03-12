# -*- coding: utf-8 -*-
__author__ = 'carl'

import functools
import json
import logging

from flask import Blueprint, request

from entity.jsonresp import JsonResponse
from web.service.data_service import get_industry
# contoller
from web.service.quantization_service import get_stks_by_cons, get_growthstockpick01_stks

iaos_blue = Blueprint('iaos_blue', __name__)


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


# default
@iaos_blue.route('/', methods=['POST', 'GET'])
@blueprintlog(log)
def main():
    # log.info("访问 %s 接口." % sys._getframe().f_code.co_name)
    return "I'm IAOS Server ~"


@iaos_blue.route('/display_industry.do', methods=['POST', 'GET'])
@blueprintlog(log)
def display_industry():
    """
    展示行业分类
    """
    return list(get_industry())


@iaos_blue.route('/sel_stks_by_cons.do', methods=['POST'])
@blueprintlog(log)
def sel_stks_by_cons():
    """
    条件选股
    进行大小盘分类、行业分类，基于此根据股票财务和行情指标进行排序，通过设置参数和过滤值筛选股票。
    具体指标包括 动态市盈率、市净率、流通股本、总市值、每股公积金、每股收益、收入同比、利润同比、毛利率、净利润率等。
    """
    if request.method == 'GET':
        return None
    else:
        condtions = request.get_data().decode()
        condtions_dict = json.loads(condtions)
        return get_stks_by_cons(condtions_dict)


@iaos_blue.route('/sel_stks_by_growthstockpick01.do', methods=['POST'])
@blueprintlog(log)
def sel_stks_by_growthstockpick01():
    if request.method == 'GET':
        return None
    else:
        condtions = request.get_data().decode()
        condtions_dict = json.loads(condtions)
        weights = condtions_dict["weights"]
        top_num = condtions_dict["top_num"]
        return get_growthstockpick01_stks(top_num=top_num, weights=weights)


@iaos_blue.errorhandler(Exception)
def error_handler(e):
    """
    全局异常捕获，也相当于一个视图函数
    """
    log_err.error("接口访问异常!%s" % e)
    return JsonResponse.error(msg=str(e))
