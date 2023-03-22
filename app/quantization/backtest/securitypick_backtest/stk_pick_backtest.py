# -*- coding: utf-8 -*-
__author__ = 'carl'

from datetime import datetime
import importlib
import os

from dateutil.relativedelta import relativedelta

from quotation.captures.tsdata_capturer import TuShareDataCapturer
from quotation.cleaning.data_clean import BaseDataClean

"""
量化选股 回测分析模块
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

    def cal_shift_period_return(self):
        """计算换仓周期中的收益"""
        now_m = datetime.today().month
        now_y = datetime.today().year
        initial_date = datetime(now_y, now_m - 1, 1)
        start_date = datetime(now_y - self.sample_periods, 1, 1)
        while start_date <= initial_date:
            print("start_date:" + str(start_date.year) + str(start_date.month).zfill(2) + str(start_date.day).zfill(2))
            end_date = start_date + relativedelta(months=+self.shift_period)
            if end_date >= initial_date:
                end_date = initial_date
            print("end_date:" + str(end_date.year) + str(end_date.month).zfill(2) + str(end_date.day).zfill(2))
            start_date_str = str(start_date.year) + str(start_date.month).zfill(2) + str(start_date.day).zfill(2)
            end_date_str = str(end_date.year) + str(end_date.month).zfill(2) + str(end_date.day).zfill(2)
            trade_start_date, trade_end_date = self.get_period_fl_trade_date(start_date=start_date_str,
                                                                             end_date=end_date_str)
            base_stocksinfos = BaseDataClean.get_certainday_base_stock_infos(trade_date=trade_start_date)
            self.init_data_func(stocksinfos=base_stocksinfos, weights=self.stk_pick_strategy_weights_args)
            stock_pool = self.get_target_stocks_func()
            print(stock_pool)

            start_date = start_date + relativedelta(months=+self.shift_period)


    def get_period_fl_trade_date(self, start_date, end_date):
        """
        获取start_date——end_date 之间最初最后一个交易日
        """
        trade_cal = self.tsdatacapture.get_trade_cal(start_date=start_date, end_date=end_date)
        start_date = trade_cal.loc[0, "cal_date"]
        end_date = trade_cal.tail(1)["cal_date"].to_list()[0]
        if int(start_date) - int(end_date) > 0:
            end_date, start_date = start_date, end_date
        return start_date, end_date
