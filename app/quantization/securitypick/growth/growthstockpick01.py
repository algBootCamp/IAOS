# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging

import numpy as np
from pandas import DataFrame

from quantization.securitypick.stock_pick import StockPick
from util.cal_util import get_data_percentile, limit_score_range

"""
成长股选股模型01：
选择处于产业生命周期成长期行业公司
公司业务高速发展，规模扩大效应明显

选择因子：
1- 股权报酬率【近一年】
    净资产收益率roe
2- 每股盈余成长率 basic_eps_yoy（体现收益和盈利的增长）
    每股收益即每股盈利（EPS），又称每股税后利润、每股盈余，指税后利润与股本总数的比率。
3- 市盈率（一定的估值安全边界）
    pe_ttm
方法：
先筛选 再打分
"""
# ----  log ------ #
log = logging.getLogger("log_quantization")
log_err = logging.getLogger("log_err")


# ----  log ------ #

class GrowthStockPick01(StockPick):

    def __init__(self):
        self.target_filter_data = None
        self.stock_pool = None
        self.stocksinfos = None
        self.weights = None

    def __filter_data(self):
        """
        筛选法，得出初步的目标数据
        roe:前70%
        basic_eps_yoy：在上一步基础上，取前35%
        pe_ttm：在上一步基础上取：该指标表现最优的10%
        """
        # list(map(int, results))
        # self.target_filter_data = self.stocksinfos.dropna(axis=0, how="any", subset=["roe", "basic_eps_yoy", "pe_ttm"])
        try:
            self.stocksinfos.drop(self.stocksinfos[np.isnan(self.stocksinfos['roe'])].index,
                                  inplace=True)
            self.stocksinfos.drop(self.stocksinfos[np.isnan(self.stocksinfos['basic_eps_yoy'])].index,
                                  inplace=True)
            self.stocksinfos.drop(self.stocksinfos[np.isnan(self.stocksinfos['pe_ttm'])].index,
                                  inplace=True)
        except Exception as e:
            log_err.error("GrowthStockPick01.stocksinfos clean Exception:{}".format(e))
            return
        # self.stocksinfos = self.stocksinfos[
        #     self.stocksinfos["roe"].str.contains("nan|Nan") == False]
        # self.stocksinfos = self.stocksinfos[
        #     self.stocksinfos["basic_eps_yoy"].str.contains("nan|Nan") == False]
        # self.stocksinfos = self.stocksinfos[
        #     self.stocksinfos["pe_ttm"].str.contains("nan | Nan") == False]
        try:
            roe_max, roe_min, roe_low, roe_mid, roe_high = get_data_percentile(
                list(map(float, np.array(self.stocksinfos.iloc[:].loc[:, 'roe']).tolist())), 30, 70, 90)
            data1 = self.stocksinfos[self.stocksinfos['roe'] >= roe_low]

            basic_eps_yoy_max, basic_eps_yoy_min, basic_eps_yoy_low, basic_eps_yoy_mid, basic_eps_yoy_high = get_data_percentile(
                list(map(float, np.array(data1.iloc[:].loc[:, 'basic_eps_yoy']).tolist())), 30, 75, 90)
            data2 = data1[data1['basic_eps_yoy'] >= basic_eps_yoy_mid]

            pe_ttm_max, pe_ttm_min, pe_ttm_low, pe_ttm_mid, pe_ttm_high = get_data_percentile(
                list(map(float, np.array(data1.iloc[:].loc[:, 'pe_ttm']).tolist())), 30, 75, 90)
            self.target_filter_data = data2[data2['pe_ttm'] <= pe_ttm_high]
        except Exception as e:
            log_err.error("GrowthStockPick01.target_filter_data gen Exception:{}".format(e))

    def __score_filter_data(self):
        """根据各个因子打分，并作和，根据总分倒序排序"""
        try:
            self.target_filter_data['roe_score'] = self.target_filter_data['roe'].rank(method='max', ascending=False)
            limit_score_range(target_range=self.weights['roe'], org_scorer_col='roe_score', df=self.target_filter_data)

            self.target_filter_data['basic_eps_yoy_score'] = self.target_filter_data['basic_eps_yoy'].rank(method='max',
                                                                                                           ascending=False)
            limit_score_range(target_range=self.weights['basic_eps_yoy'], org_scorer_col='basic_eps_yoy_score',
                              df=self.target_filter_data)

            self.target_filter_data['pe_ttm_score'] = self.target_filter_data['pe_ttm'].rank(method='max',
                                                                                             ascending=False)
            limit_score_range(target_range=self.weights['pe_ttm'], org_scorer_col='pe_ttm_score',
                              df=self.target_filter_data)
            self.target_filter_data['sum_score'] = self.target_filter_data[
                ["roe_score", "basic_eps_yoy_score", "pe_ttm_score"]].sum(axis=1)
            self.target_filter_data.sort_values(by="sum_score", ascending=False, inplace=True)
        except Exception as e:
            log_err.error("GrowthStockPick01.score_filter_data Exception:{}".format(e))

    def init_data(self, stocksinfos: DataFrame, weights={'roe': 34, 'basic_eps_yoy': 33, 'pe_ttm': 33}):
        self.stocksinfos = stocksinfos.copy(deep=True)
        self.weights = weights

    def get_target_stock_pool(self, top_num: int = 5):
        """
        获取该模型下得到的股票池
        """
        self.__filter_data()
        self.__score_filter_data()
        if self.target_filter_data is None or len(self.target_filter_data.index) == 0:
            log.info("GrowthStockPick01 has no stock_pool!")
            return None
        if top_num > 0:
            self.target_filter_data = self.target_filter_data.head(top_num)
        self.stock_pool = {}
        for index, row in self.target_filter_data.iterrows():
            symbol = row['symbol']
            self.stock_pool[symbol] = row.to_dict()
        log.info("GrowthStockPick01 top{} stock_pool: {}".format(top_num, self.stock_pool.keys()))
        return self.stock_pool
