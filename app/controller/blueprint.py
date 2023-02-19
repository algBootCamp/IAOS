# -*- coding: utf-8 -*-
__author__ = 'carl'

import json

from flask import Blueprint, request, render_template, session, Response, redirect

# noinspection SpellCheckingInspection
from quantization.securitypick.stockpick01 import StockPick01

'''contoller'''
blue = Blueprint('blue', __name__)
'''
进行大小盘分类、行业分类，基于此根据股票财务和行情指标进行排序，通过设置参数和过滤值筛选股票。
具体指标包括 动态市盈率、市净率、流通股本、总市值、每股公积金、每股收益、收入同比、利润同比、毛利率、净利润率等。
'''
stkp01: StockPick01 = StockPick01()


@blue.route('/display_industry.do', methods=['POST', 'GET'])  # url路由
def display_industry()->str:
    '''
    展示行业分类
    '''
    return json.dumps(list(stkp01.industry_set))

