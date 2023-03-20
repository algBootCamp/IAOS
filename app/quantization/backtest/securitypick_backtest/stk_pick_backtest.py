# -*- coding: utf-8 -*-
__author__ = 'carl'

import importlib
import os

"""
量化选股 回测分析模块
"""


class SecurityPickBackTest(object):
    def __init__(self, stk_pick_strategy_mod='growthstockpick01',
                 stk_pick_strategy_cls='GrowthStockPick01',
                 benchmark: str = "000001.SH",
                 sample_periods: int = 7,
                 shift_period: float = 1.0):
        """
        stk_pick_strategy_mod_name:回测的选股策略模型对应模块
        stk_pick_strategy_cls_name:回测的选股策略模型对应类
        benchmark：     对标基准
        sample_periods：回测周期（年）
        shift_period：  换仓周期（年）
        """
        self.get_target_stocks_func = 'get_target_stock_pool'
        self.init_data_func = 'init_data'
        self.stk_pick_strategy_mod_name = stk_pick_strategy_mod
        self.stk_pick_strategy_cls_name = stk_pick_strategy_cls
        self.strategy_mod = None
        self.strategy_cls = None
        self.strategy_instance = None
        self.benchmark = benchmark
        self.sample_periods = sample_periods
        self.shift_period = shift_period

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
