# -*- coding: utf-8 -*-
__author__ = 'carl'

import time

import pandas as pd
from pandas import DataFrame, Series

from db.myredis.redis_cli import RedisClient
from entity.singleton import Singleton
from quotation.captures.tsdata_capturer import TuShareDataCapturer

"""
因子有效性校验：
针对每个候选因子

0- 获取股票池，取近7年内均有数据的股票，以此为基准
1- 选择最近7年（每年每个月月中的数据）内每个股票数据
2- 每个月中计算每只股票的 因子X ，并排序打分，分为5组
3- 计算因子X在5个分组中的 年化复合收益率、超额收益、收益与分值相关性
"""


# noinspection DuplicatedCode,PyRedundantParentheses,PyListCreation,PyNoneFunctionAssignment
class FactorValidityCheck(Singleton):

    def __init__(self, factors: list = None, sample_periods: int = 7):
        self.rediscli = RedisClient().get_redis_cli()
        self.tsdatacapture: TuShareDataCapturer = TuShareDataCapturer()
        self.factors = factors
        self.sample_periods = sample_periods
        if not self.factors:
            self.default_factors()
        self.factors_ics = DataFrame()
        now_time = time.localtime(time.time())
        self.this_year = now_time.tm_year
        self.this_month = now_time.tm_mon
        self.sample_years = list(reversed([str(self.this_year - i) for i in range(self.sample_periods+1)]))
        self.sample_months = None
        self.init_sample_months()

    def cal_factors_ic(self):
        """
        计算因子与年化收益的相关性 IC
        """
        factors_ics_dict = {}
        for factor in self.factors:
            factor_annual_return = self.cal_ports_annual_return(factor=factor)
            ic = factor_annual_return[0:5].corr(Series([1, 2, 3, 4, 5], index=factor_annual_return[0:5].index))
            factors_ics_dict[factor] = [ic]
        self.factors_ics = pd.DataFrame(factors_ics_dict).T

    def cal_ports_annual_return(self, factor="pe_ttm"):
        """
        计算某一个因子在各个分组的平均年化收益
        """
        port_profit = {}
        mon_num = 0
        for y in self.sample_years:
            if y == str(self.this_year):
                if self.this_month == 1:
                    break
                # 记得一个因子计算完之后 重新赋值
                self.sample_months.clear()
                mend = self.this_month - 1
                for m in range(1, mend + 1):
                    self.sample_months[str(m).zfill(2)] = str(m + 1).zfill(2)
                    if m == 12:
                        self.sample_months[str(m).zfill(2)] = str(m).zfill(2)
            for mstart, mend in self.sample_months.items():
                mon_num += 1
                start_date = y + mstart + "01"
                end_date = y + mend + "01"
                if mstart == "12":
                    end_date = y + mend + "31"

                trade_cal = self.tsdatacapture.get_trade_cal(start_date=start_date, end_date=end_date)
                start_date = trade_cal.loc[0, "cal_date"]
                end_date = trade_cal.tail(1)["cal_date"].to_list()[0]
                if int(start_date) - int(end_date) > 0:
                    end_date, start_date = start_date, end_date

                basics_data: DataFrame = self.tsdatacapture.get_daily_basic(trade_date=start_date)[[
                    'ts_code', 'circ_mv', factor]]

                basics_data.dropna(axis=0, how='any', subset=[factor], inplace=True)
                score = basics_data[['ts_code', factor]].sort_values(by=factor)

                # 流通市值
                cmv = basics_data[['ts_code', 'circ_mv']].sort_values(by='ts_code')
                cmv.index = cmv['ts_code']
                port1 = list(score['ts_code'])[: len(score.index) // 5]
                port2 = list(score['ts_code'])[len(score.index) // 5: 2 * len(score.index) // 5]
                port3 = list(score['ts_code'])[2 * len(score.index) // 5: -2 * len(score.index) // 5]
                port4 = list(score['ts_code'])[-2 * len(score.index) // 5: -len(score.index) // 5]
                port5 = list(score['ts_code'])[-len(score.index) // 5:]
                ports = [port1, port2, port3, port4, port5]
                port_index = 0
                for port in ports:
                    port_index += 1
                    weighted_m_return = self.cal_port_monthly_return(port, start_date, end_date, cmv)
                    if not port_profit.keys().__contains__("port_" + str(port_index)):
                        prof_list = []
                        prof_list.append(weighted_m_return)
                        port_profit["port_" + str(port_index)] = prof_list
                    else:
                        port_profit["port_" + str(port_index)].append(weighted_m_return)
        final_port_i = pd.DataFrame(port_profit)
        # to see https://zhuanlan.zhihu.com/p/390849319
        # 复利的本息计算公式是：F=P（1+i)^n P=本金，i=利率，n=期限
        # 总收益 此处以1为本金
        total_return = (final_port_i + 1).cumprod().iloc[-1, :]
        # 平均年化收益
        annual_return = (total_return) ** (1. / (mon_num / 12)) - 1
        # 重新赋值  sample_months
        self.init_sample_months()
        return annual_return

    def cal_port_monthly_return(self, port, startdate, enddate, CMV):
        """
        计算分组内流通市值加权的月收益率
        """
        close1 = self.get_close(port, startdate)
        c1_list = close1['ts_code'].to_list()
        close2 = self.get_close(port, enddate)
        c2_list = close2['ts_code'].to_list()
        valid_codes = list(set(c1_list).intersection(set(c2_list)))
        close1 = close1['close'].loc[valid_codes]
        close2 = close2['close'].loc[valid_codes]
        # 组合月收益率集合
        month_profit = close2 / close1 - 1
        circ_mv = CMV['circ_mv'].loc[valid_codes]
        # 月收益率加权流通市值
        weighted_month_profit = month_profit * circ_mv
        # 根据流通市值加权的月收益率
        weighted_m_return = weighted_month_profit.sum() / circ_mv.sum()
        return weighted_m_return

    def get_close(self, port, trade_date):
        """
        获取分组内收盘价
        """
        symbol = ","
        close = DataFrame()
        # 缓解压力 大于500个 分割
        if len(port) > 500:
            f = lambda a: map(lambda b: a[b:b + 300], range(0, len(a), 300))
            part_ports = f(port)
            for part_port in part_ports:
                ts_codes = symbol.join(part_port)
                # 当且仅当 start_date=end_date  ts_code可传多值
                close = close.append(
                    other=self.tsdatacapture.get_pro_bar(ts_code=ts_codes, start_date=trade_date, end_date=trade_date))
        else:
            ts_codes = symbol.join(port)
            # 当且仅当 start_date=end_date  ts_code可传多值
            close = self.tsdatacapture.get_pro_bar(ts_code=ts_codes, start_date=trade_date, end_date=trade_date)
        # 实在没办法了 一个一个取 防止多值获取失败
        if close is None or close.empty:
            for ts_code in port:
                close = close.append(
                    other=self.tsdatacapture.get_pro_bar(ts_code=ts_code, start_date=trade_date, end_date=trade_date))
        close = close[['ts_code', 'close']]
        close.index = close['ts_code']
        return close

    def init_sample_months(self):
        self.sample_months = {'01': '02', '02': '03', '03': '04', '04': '05',
                              '05': '06', '06': '07', '07': '08', '08': '09',
                              '09': '10', '10': '11', '11': '12', '12': '12'}

    def default_factors(self):
        """默认因子集"""
        self.factors = ['turnover_rate', 'turnover_rate_f',
                        'volume_ratio', 'pe', 'pe_ttm', 'pb', 'ps',
                        'ps_ttm', 'total_share', 'float_share', 'total_mv',
                        'circ_mv', 'dv_ratio', 'dv_ttm']
