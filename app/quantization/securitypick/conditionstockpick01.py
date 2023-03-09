# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging

import pandas as pd
from pandas import DataFrame

from quantization.securitypick.conditonstockpick import ConditonStockPick
from quotation.cache.cache import LocalBasicDataCache
from util.obj_util import method_call

'''
条件选股01:基于 base_stock_infos 数据进行选股
'''
# ----  log ------ #
log = logging.getLogger("log_quantization")
log_err = logging.getLogger("log_err")


# ----  log ------ #

# TODO list_date', 'ann_date', 'end_date', 未检索
# noinspection DuplicatedCode,PyUnusedLocal
class ConditonStockPick01(ConditonStockPick):

    def __init__(self):
        """ 预备数据 base_stock_infos """
        self.base_stock_infos = LocalBasicDataCache.base_stock_infos
        if self.base_stock_infos is None:
            self.base_stock_infos = LocalBasicDataCache.load_base_stock_infos()

    def get_target_data(self, **condtions) -> DataFrame:
        condtions_col = ['ts_code', 'symbol', 'name', 'area', 'industry', 'market', 'list_date', 'exchange',
                         'pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm', 'total_share', 'float_share', 'total_mv', 'circ_mv',
                         'dv_ratio', 'dv_ttm', 'changepercent', 'trade', 'volume', 'turnoverratio', 'amount',
                         'ann_date', 'end_date', 'eps', 'current_ratio', 'quick_ratio', 'bps',
                         'netprofit_margin', 'grossprofit_margin', 'profit_to_gr', 'op_of_gr', 'roe',
                         'roa', 'npta', 'roic', 'roe_yearly', 'roa2_yearly', 'debt_to_assets', 'op_yoy',
                         'ebt_yoy', 'tr_yoy', 'or_yoy', 'equity_yoy', 'update_flag'
                         ]
        condtions_name = ['TS股票代码', '股票代码', '股票名称', '地区', '行业', '市场', '上市日期', '交易所',
                          '市盈率', '市盈率TTM', '市净率', '市销率', '市销率TTM', '总股本', '流通股本', '总市值', '流通市值',
                          '股息率', '股息率TTM', '涨跌幅', '现价', '成交量', '换手率', '成交额',
                          '公告日期', '报告期', '基本每股收益', '流动比率', '速动比率', '每股净资产', '销售净利率',
                          '销售毛利率', '净利润率', '营业利润率', '净资产收益率', '总资产报酬率', '总资产净利润', '投入资本回报率', '年化净资产收益率',
                          '年化总资产报酬率', '资产负债率', '营业利润同比增长率', '利润总额同比增长率', '营业总收入同比增长率', '营业收入同比增长率', '净资产同比增长率', '更新标识'
                          ]
        # enable_condtions_dict = dict(zip(condtions_col, condtions_name))
        condtions_dict = dict()
        # 条件校验
        for condtion_key, condtion in condtions.items():
            if condtions_col.__contains__(condtion_key):
                condtions_dict[condtion_key] = condtion
            else:
                log.warning("ConditonStockPick01 not support [{}] conditional retrieval!".format(condtion_key))

        return self.__retrieval_data(condtions_dict)

    def __retrieval_data(self, condtions_dict) -> DataFrame:
        data: DataFrame = None
        for condtion_key, condtion in condtions_dict.items():
            if data is not None:
                data = pd.merge(data, method_call(self, "_ConditonStockPick01__" + condtion_key, condtion), how="inner")
            else:
                data = method_call(self, "_ConditonStockPick01__" + condtion_key, condtion)
        return data

    def __symbol(self, symbol):
        data = self.base_stock_infos.query("symbol=='{}'".format(symbol))
        return data

    def __name(self, name):
        data = self.base_stock_infos.query("name=='{}'".format(name))
        return data

    def __area(self, area):
        data = self.base_stock_infos.query("area=='{}'".format(area))
        return data

    def __industry(self, industry):
        data = self.base_stock_infos.query("industry=='{}'".format(industry))
        return data

    def __market(self, market):
        data = self.base_stock_infos.query("market=='{}'".format(market))
        return data

    def __exchange(self, exchange):
        data = self.base_stock_infos.query("exchange=='{}'".format(exchange))
        return data

    def __pe(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[(self.base_stock_infos["pe"] >= min_val) & (self.base_stock_infos["pe"] < max_val)]
        return data

    def __pe_ttm(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["pe_ttm"] >= min_val) & (self.base_stock_infos["pe_ttm"] < max_val)]
        return data

    def __pb(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[(self.base_stock_infos["pb"] >= min_val) & (self.base_stock_infos["pb"] < max_val)]
        return data

    def __ps(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[(self.base_stock_infos["ps"] >= min_val) & (self.base_stock_infos["ps"] < max_val)]
        return data

    def __ps_ttm(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["ps_ttm"] >= min_val) & (self.base_stock_infos["ps_ttm"] < max_val)]
        return data

    def __total_share(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["total_share"] >= min_val) & (self.base_stock_infos["total_share"] < max_val)]
        return data

    def __float_share(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["float_share"] >= min_val) & (self.base_stock_infos["float_share"] < max_val)]
        return data

    def __total_mv(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["total_mv"] >= min_val) & (self.base_stock_infos["total_mv"] < max_val)]
        return data

    def __circ_mv(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["circ_mv"] >= min_val) & (self.base_stock_infos["circ_mv"] < max_val)]
        return data

    def __dv_ratio(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["dv_ratio"] >= min_val) & (self.base_stock_infos["dv_ratio"] < max_val)]
        return data

    def __dv_ttm(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["dv_ttm"] >= min_val) & (self.base_stock_infos["dv_ttm"] < max_val)]
        return data

    def __changepercent(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["changepercent"] >= min_val) & (self.base_stock_infos["changepercent"] < max_val)]
        return data

    def __trade(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["trade"] >= min_val) & (self.base_stock_infos["trade"] < max_val)]
        return data

    def __volume(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["volume"] >= min_val) & (self.base_stock_infos["volume"] < max_val)]
        return data

    def __turnoverratio(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["turnoverratio"] >= min_val) & (self.base_stock_infos["turnoverratio"] < max_val)]
        return data

    def __amount(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["amount"] >= min_val) & (self.base_stock_infos["amount"] < max_val)]
        return data

    def __eps(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["eps"] >= min_val) & (self.base_stock_infos["eps"] < max_val)]
        return data

    def __current_ratio(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["current_ratio"] >= min_val) & (self.base_stock_infos["current_ratio"] < max_val)]
        return data

    def __quick_ratio(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["quick_ratio"] >= min_val) & (self.base_stock_infos["quick_ratio"] < max_val)]
        return data

    def __bps(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["bps"] >= min_val) & (self.base_stock_infos["bps"] < max_val)]
        return data

    def __netprofit_margin(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["netprofit_margin"] >= min_val) & (
                    self.base_stock_infos["netprofit_margin"] < max_val)]
        return data

    def __grossprofit_margin(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["grossprofit_margin"] >= min_val) & (
                    self.base_stock_infos["grossprofit_margin"] < max_val)]
        return data

    def __profit_to_gr(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["profit_to_gr"] >= min_val) & (
                    self.base_stock_infos["profit_to_gr"] < max_val)]
        return data

    def __op_of_gr(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["op_of_gr"] >= min_val) & (
                    self.base_stock_infos["op_of_gr"] < max_val)]
        return data

    def __roe(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["roe"] >= min_val) & (self.base_stock_infos["roe"] < max_val)]
        return data

    def __roa(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["roa"] >= min_val) & (self.base_stock_infos["roa"] < max_val)]
        return data

    def __npta(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["npta"] >= min_val) & (self.base_stock_infos["npta"] < max_val)]
        return data

    def __roic(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["roic"] >= min_val) & (self.base_stock_infos["roic"] < max_val)]
        return data

    def __roe_yearly(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["roe_yearly"] >= min_val) & (self.base_stock_infos["roe_yearly"] < max_val)]
        return data

    def __roa2_yearly(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["roa2_yearly"] >= min_val) & (self.base_stock_infos["roa2_yearly"] < max_val)]
        return data

    def __debt_to_assets(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["debt_to_assets"] >= min_val) & (self.base_stock_infos["debt_to_assets"] < max_val)]
        return data

    def __op_yoy(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["op_yoy"] >= min_val) & (self.base_stock_infos["op_yoy"] < max_val)]
        return data

    def __ebt_yoy(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["ebt_yoy"] >= min_val) & (self.base_stock_infos["ebt_yoy"] < max_val)]
        return data

    def __tr_yoy(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["tr_yoy"] >= min_val) & (self.base_stock_infos["tr_yoy"] < max_val)]
        return data

    def __or_yoy(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["or_yoy"] >= min_val) & (self.base_stock_infos["or_yoy"] < max_val)]
        return data

    def __equity_yoy(self, val: list):
        min_val = val[0]
        max_val = val[1]
        data = self.base_stock_infos[
            (self.base_stock_infos["equity_yoy"] >= min_val) & (self.base_stock_infos["equity_yoy"] < max_val)]
        return data
