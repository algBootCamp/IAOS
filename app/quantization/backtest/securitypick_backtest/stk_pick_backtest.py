# -*- coding: utf-8 -*-
__author__ = 'carl'

import importlib
import os
from datetime import datetime

from dateutil.relativedelta import relativedelta

from quotation.captures.tsdata_capturer import TuShareDataCapturer
from quotation.cleaning.data_clean import BaseDataClean
from util.quant_util import get_price, get_period_fl_trade_date

"""
量化选股 回测分析模块

评判指标：
累积收益
年化复合收益
年化超额收益
跑赢基准周期占比
正收益周期占比
"""


# noinspection DuplicatedCode
class SecurityPickBackTest(object):
    def __init__(self, stk_pick_strategy_mod='growthstockpick01',
                 stk_pick_strategy_cls='GrowthStockPick01',
                 benchmark: str = "000001.SH",
                 sample_periods: int = 7,
                 shift_period: float = 6,
                 **stk_pick_strategy_weights_args):
        """
        stk_pick_strategy_mod_name:回测的选股策略模型对应模块
        stk_pick_strategy_cls_name:回测的选股策略模型对应类
        stk_pick_strategy_weights_args:回测的选股策略模型对应因子权重
        benchmark：     对标基准
        sample_periods：回测周期（年）
        shift_period：  换仓周期（月）
        """
        self.get_target_stocks_func_name = 'get_target_stock_pool'
        self.init_data_func_name = 'init_data'
        self.stk_pick_strategy_mod_name = stk_pick_strategy_mod
        self.stk_pick_strategy_cls_name = stk_pick_strategy_cls
        self.stk_pick_strategy_weights_args = stk_pick_strategy_weights_args
        self.strategy_mod = None
        self.strategy_cls = None
        self.strategy_instance = None
        self.init_data_func = None
        self.get_target_stocks_func = None

        self.benchmark = benchmark
        self.sample_periods = sample_periods
        self.shift_period = shift_period
        self.tsdatacapture: TuShareDataCapturer = TuShareDataCapturer()

    def init_stk_pick_strategy(self):
        securitypick_path = r"app/quantization/securitypick/"
        path = os.getcwd()
        path = path[:path.index("app")] + securitypick_path
        pkg = None
        for root, dirs, files in os.walk(path):
            for file in files:
                # 获取文件路径
                if "__init__" in file:
                    continue
                if "__pycache__" in root:
                    continue
                file_s = os.path.join(root, file)
                res = self.stk_pick_strategy_mod_name in file_s
                if res:
                    pkg = root.split(r"/")[-1]
                    break
        self.strategy_mod = importlib.import_module(
            "quantization.securitypick.%s.%s" % (pkg, self.stk_pick_strategy_mod_name))
        self.strategy_cls = getattr(self.strategy_mod, self.stk_pick_strategy_cls_name)
        self.strategy_instance = self.strategy_cls()
        self.init_data_func = getattr(self.strategy_instance, self.init_data_func_name)
        self.get_target_stocks_func = getattr(self.strategy_instance, self.get_target_stocks_func_name)

    def cal_all_period_return(self):
        """计算所有换仓周期中的收益"""
        now_m = datetime.today().month
        now_y = datetime.today().year
        now_date = datetime(now_y, now_m, 1)
        start_date = datetime(now_y - self.sample_periods, 1, 1)
        while start_date < now_date:
            end_date = start_date + relativedelta(months=+self.shift_period)
            if end_date >= now_date:
                end_date = now_date
            start_date_str = str(start_date.year) + str(start_date.month).zfill(2) + str(start_date.day).zfill(2)
            end_date_str = str(end_date.year) + str(end_date.month).zfill(2) + str(end_date.day).zfill(2)
            trade_start_date, trade_end_date = get_period_fl_trade_date(start_date=start_date_str,
                                                                        end_date=end_date_str)
            print(start_date_str, "---", end_date_str)
            # 根据流通市值加权的持仓周期收益率
            weighted_p_return = self.cal_shift_period_return(trade_start_date=trade_start_date,
                                                             trade_end_date=trade_end_date)
            benchmark_p_return = self.cal_benchmark_shift_period_return(startdate=trade_start_date,
                                                                        enddate=trade_end_date)
            print("weighted_p_return:  ", weighted_p_return)
            print("benchmark_p_return: ", benchmark_p_return)
            print("----------------------------------------")
            start_date = end_date

    def cal_benchmark_shift_period_return(self, startdate, enddate):
        """
        计算特定换仓周期内基准的月收益率
        """
        close1 = get_price(ts_code_list=[self.benchmark], trade_date=startdate, asset='I')
        close2 = get_price(ts_code_list=[self.benchmark], trade_date=enddate, asset='I')
        c1_list = close1['ts_code'].to_list()
        c2_list = close2['ts_code'].to_list()
        valid_codes = list(set(c1_list).intersection(set(c2_list)))
        close1 = close1['close'].loc[valid_codes]
        close2 = close2['close'].loc[valid_codes]
        benchmark_return = (close2 / close1 - 1).sum()
        return benchmark_return

    def cal_shift_period_return(self, trade_start_date, trade_end_date):
        """计算特定换仓周期中的收益"""
        base_stocksinfos = BaseDataClean.get_certainday_base_stock_infos(trade_date=trade_start_date)
        self.init_data_func(stocksinfos=base_stocksinfos, weights=self.stk_pick_strategy_weights_args)
        target_filter_data = self.get_target_stocks_func()
        stock_pool = target_filter_data['ts_code'].to_list()
        print("stock_pool: ", stock_pool)
        # 流通市值
        cmv = target_filter_data[['ts_code', 'circ_mv']].sort_values(by='ts_code')
        cmv.index = cmv['ts_code']
        close1 = get_price(ts_code_list=stock_pool, trade_date=trade_start_date, asset='E')
        close2 = get_price(ts_code_list=stock_pool, trade_date=trade_end_date, asset='E')
        c1_list = close1['ts_code'].to_list()
        c2_list = close2['ts_code'].to_list()
        valid_codes = list(set(c1_list).intersection(set(c2_list)))
        close1 = close1['close'].loc[valid_codes]
        close2 = close2['close'].loc[valid_codes]
        # 组合持仓周期内收益率集合
        period_profit = close2 / close1 - 1
        circ_mv = cmv['circ_mv'].loc[valid_codes]
        # 持仓周期收益率加权流通市值
        weighted_period_profit = period_profit * circ_mv
        # 根据流通市值加权的持仓周期收益率
        weighted_p_return = weighted_period_profit.sum() / circ_mv.sum()
        return weighted_p_return
