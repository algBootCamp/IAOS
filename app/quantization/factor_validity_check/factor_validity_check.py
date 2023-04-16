# -*- coding: utf-8 -*-
__author__ = 'carl'

import time
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas import DataFrame, Series

from db.mymysql.mysql_helper import MySqLHelper
from db.myredis.redis_cli import RedisClient
from entity.singleton import Singleton
from quotation.captures.tsdata_capturer import TuShareDataCapturer
from quotation.cleaning.data_clean import BaseDataClean
from util.quant_util import get_price, get_period_fl_trade_date

warnings.filterwarnings("ignore")

"""
因子有效性校验：
目前该模块支持 BaseDataClean.get_certainday_base_stock_infos 返回字段的校验;
继承复写重写 get_factor_data 即可;
默认取上证指数 000001.SH 为对比 基准;

针对每个候选因子:
0- 获取股票池，取近7年内均有数据的股票，以此为基准
1- 选择最近7年（每年每个月月中的数据）内每个股票数据
2- 每个月中计算每只股票的 因子X ，并排序打分，分为5组
3- 计算因子X在5个分组中的 年化复合收益率、超额收益、收益与分值相关性

检验有效性的量化标准：
1- 序列1-n的组合，年化复合收益应满足一定排序关系，即组合因子大小与收益具有较大相关关系。
假定序列i的组合年化收益为Xi,则Xi与i的相关性绝对值Abs(Corr(Xi,i))>min_corr。此处min_corr为给定的最小相关阀值。

2- 序列1和n表示的两个极端组合超额收益分别为AR1、ARn。min_top、min_bottom 表示最小超额收益阀值。
if AR1 > ARn #因子越小，收益越大
则应满足AR1 > min_top >0 and ARn < min_bottom < 0
if AR1 < ARn #因子越小，收益越大
则应满足ARn > min_top >0 and AR1 < min_bottom < 0
以上条件保证因子最大和最小的两个组合，一个明显跑赢市场，一个明显跑输市场。

3- 在任何市场行情下，1和n两个极端组合，都以较高概率跑赢or跑输市场。
以上三个条件，可以选出过去一段时间有较好选股能力的因子。


评判指标：
组合累积收益
因子平均年化收益
因子年化超额收益
高收益组合跑赢概率
低收益组合跑输概率
正收益月占比
因子IC
"""


# noinspection DuplicatedCode,PyRedundantParentheses,PyListCreation,PyNoneFunctionAssignment,PyMethodMayBeStatic
class FactorValidityCheck(Singleton):

    def __init__(self, benchmark: str = "000001.SH", factors: list = None, sample_periods: int = 7):
        self.rediscli = RedisClient().get_redis_cli()
        self.db = MySqLHelper()
        self.tsdatacapture: TuShareDataCapturer = TuShareDataCapturer()
        self.benchmark = benchmark
        self.factors = factors
        self.sample_periods = sample_periods
        if not self.factors:
            self.default_factors()
        now_time = time.localtime(time.time())
        self.this_year = now_time.tm_year
        self.this_month = now_time.tm_mon
        self.sample_years = list(reversed([str(self.this_year - i) for i in range(self.sample_periods + 1)]))
        self.sample_months = None
        self.init_sample_months()

        # factors ic
        self.factors_ics = DataFrame()
        # factor ic最小相关阀值
        self.min_corr = 0.5
        # 最小超额收益阀值
        self.min_bottom = -0.05
        # 最小超额收益阀值
        self.min_top = 0.05

        # 因子分组月收益
        self.monthly_return = DataFrame()
        # 因子总收益
        self.total_return = {}
        # 因子平均年化收益
        self.annual_return = {}
        # 超额收益
        self.excess_return = {}
        # 赢家组合跑赢概率
        self.win_prob = {}
        # 输家组合跑输概率
        self.loss_prob = {}
        # effect_test["ic"]记录因子相关性，>0.5或<-0.5合格
        # effect_test["excess"]记录 赢家组合超额收益，输家组合超额收益
        # effect_test["prob"]记录 赢家组合跑赢概率和输家组合跑输概率;【>0.5,>0.4】合格(因实际情况，跑输概率暂时不考虑)
        self.effect_test = {}
        self.effect_test_df = None
        # 符合 检验有效性的量化标准 的因子
        self.effective_factors = None

    def get_validity_all_factors(self):
        """
        获取 符合 检验有效性的量化标准 的因子
        """
        if not self.effect_test_df:
            self.check_all_factor_validity()

    def check_factor_validity(self, fac):
        """检验有效性的量化标准"""
        # 获取特定因子指定周期内月收益
        self.gather_monthly_return(fac)
        # 计算特定因子评判指标
        self.effect_test[fac] = {}
        monthly = self.monthly_return[[fac]]
        # 计算因子平均年化收益
        # to see https://zhuanlan.zhihu.com/p/390849319
        # 复利的本息计算公式是：F=P（1+i)^n P=本金，i=利率，n=期限
        fac_total_return = (monthly + 1).T.cumprod().iloc[-1, :] - 1
        self.total_return[fac] = fac_total_return
        # 各个组合平均年化收益
        fac_annual_return = (self.total_return[fac] + 1) ** (1. / (len(monthly) / 12)) - 1
        self.annual_return[fac] = fac_annual_return
        # 各个组合超额收益 【因子annual_return - 基准annual_return】
        fac_excess_return = self.annual_return[fac] - self.annual_return[fac][-1]
        self.excess_return[fac] = fac_excess_return
        # 判断因子有效性
        # 1.年化收益与因子的相关性IC
        fac_ic = self.annual_return[fac][0:5].corr(
            Series([1, 2, 3, 4, 5], index=self.annual_return[fac][0:5].index))
        self.effect_test[fac]["ic"] = fac_ic

        # 2.高收益组合跑赢概率  port_1因子<port_5因子
        # 因子小，收益小，port_1是输家组合，port_5是赢家组合
        if self.total_return[fac][0] < self.total_return[fac][-2]:
            loss_excess = monthly.iloc[0, :] - monthly.iloc[-1, :]
            self.loss_prob[fac] = loss_excess[loss_excess < 0].count() / float(len(loss_excess))
            win_excess = monthly.iloc[-2, :] - monthly.iloc[-1, :]
            self.win_prob[fac] = win_excess[win_excess > 0].count() / float(len(win_excess))
            # 赢家组合跑赢概率和输家组合跑输概率
            self.effect_test[fac]["prob"] = [self.win_prob[fac], self.loss_prob[fac]]
            # 超额收益
            self.effect_test[fac]["excess"] = [self.excess_return[fac][-2] * 100, self.excess_return[fac][0] * 100]
            l_annual_return = fac_annual_return["port_1"]
            w_annual_return = fac_annual_return["port_5"]
            l_total_return = fac_total_return["port_1"]
            w_total_return = fac_total_return["port_5"]
        # 因子小，收益大，port_1是赢家组合，port_5是输家组合
        else:
            # port_5-benchmark
            loss_excess = monthly.iloc[-2, :] - monthly.iloc[-1, :]
            self.loss_prob[fac] = loss_excess[loss_excess < 0].count() / float(len(loss_excess))
            win_excess = monthly.iloc[0, :] - monthly.iloc[-1, :]
            self.win_prob[fac] = win_excess[win_excess > 0].count() / float(len(win_excess))
            # 赢家组合跑赢概率和输家组合跑输概率
            self.effect_test[fac]["prob"] = [self.win_prob[fac], self.loss_prob[fac]]
            # 超额收益
            self.effect_test[fac]["excess"] = [self.excess_return[fac][0] * 100, self.excess_return[fac][-2] * 100]
            l_annual_return = fac_annual_return["port_5"]
            w_annual_return = fac_annual_return["port_1"]
            l_total_return = fac_total_return["port_5"]
            w_total_return = fac_total_return["port_1"]
        self.effect_test_df = (DataFrame(self.effect_test))
        self.effective_factors = self.effect_test_df.copy(deep=True)

        self.save_fac_valid_info(fac, fac_annual_return, fac_ic, fac_total_return, l_annual_return, l_total_return,
                                 w_annual_return, w_total_return)

    def check_all_factor_validity(self):
        """检验有效性的量化标准"""
        for fac in self.factors:
            self.check_factor_validity(fac=fac)

    def gather_monthly_return(self, factor):
        """
        集合 monthly_return
        """
        flag = 0
        factor_port_profit = self.cal_factor_ports_monthly_return(factor=factor)
        fac_port_profit = DataFrame(factor_port_profit).T
        columns = pd.MultiIndex.from_product([[factor], fac_port_profit.columns])
        fac_port_profit.columns = columns
        if flag == 0:
            self.monthly_return = fac_port_profit
        else:
            self.monthly_return = self.monthly_return.join(fac_port_profit)
        flag += 1
        del flag

    def cal_factor_ports_monthly_return(self, factor="pe_ttm"):
        """
        计算某一个因子在各个分组的月收益率
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
                start = time.time()
                mon_num += 1
                start_date = y + mstart + "01"
                end_date = y + mend + "01"
                if mstart == "12":
                    end_date = y + mend + "31"

                start_date, end_date = get_period_fl_trade_date(start_date, end_date)
                # 获取指标数据 可重写的方法 【必含字段 'ts_code', 'circ_mv', factor】
                basics_data = self.get_factor_data(factor, start_date)
                # 分组 并计算 分组月收益
                self.part_data_cal_mon_profit(basics_data, end_date, factor, port_profit, start_date)

                # 计算基准月收益
                benchmark_m_return = self.cal_benchmark_monthly_return(start_date, end_date)
                if not port_profit.keys().__contains__("benchmark"):
                    prof_list = []
                    prof_list.append(benchmark_m_return)
                    port_profit["benchmark"] = prof_list
                else:
                    port_profit["benchmark"].append(benchmark_m_return)
                end = time.time()
                use_time = end - start
                print('month data 运行时间为: %s Seconds' % (use_time))
        self.init_sample_months()
        return port_profit

    def part_data_cal_mon_profit(self, basics_data, end_date, factor, port_profit, start_date):
        """分组 并计算 分组月收益"""
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

    def get_factor_data(self, factor, trade_date):
        """
        获取含有因子数据的行情
        如果所需因子不在 get_certainday_base_stock_infos 需要重写该方法
        """
        # start = time.time()
        basics_data: DataFrame = BaseDataClean.get_certainday_base_stock_infos(trade_date=trade_date)[[
            'ts_code', 'circ_mv', factor]]
        basics_data.dropna(axis=0, how='any', subset=[factor], inplace=True)
        # end = time.time()
        # use_time=end - start
        # print('get_factor_data 运行时间为: %s Seconds' % (use_time))
        return basics_data

    def cal_port_monthly_return(self, port, startdate, enddate, CMV):
        """
        计算分组内流通市值加权的月收益率
        """
        close1 = get_price(port, startdate)
        c1_list = close1['ts_code'].to_list()
        close2 = get_price(port, enddate)
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

    def cal_benchmark_monthly_return(self, startdate, enddate):
        """
        计算分组内基准的月收益率
        """
        close1 = get_price([self.benchmark], startdate, asset='I')
        close2 = get_price([self.benchmark], enddate, asset='I')
        c1_list = close1['ts_code'].to_list()
        c2_list = close2['ts_code'].to_list()
        valid_codes = list(set(c1_list).intersection(set(c2_list)))
        close1 = close1['close'].loc[valid_codes]
        close2 = close2['close'].loc[valid_codes]
        benchmark_return = (close2 / close1 - 1).sum()
        return benchmark_return

    def save_fac_valid_info(self, fac, fac_annual_return, fac_ic, fac_total_return, l_annual_return, l_total_return,
                            w_annual_return, w_total_return):
        """
        保存因子有效性信息
        """
        sql1 = r'select * from candidate_factors where factor_id=%s'
        args = fac
        res = self.db.selectone(sql=sql1, param=args)
        factor_id = res[1]
        factor_name = res[2]
        factor_type_id = res[3]
        factor_type = res[4]
        benchmark = self.benchmark
        benchmark_name = ''
        benchmark_total_return = fac_total_return["benchmark"]
        benchmark_annual_return = fac_annual_return["benchmark"]
        win_total_return = w_total_return
        win_annual_return = w_annual_return
        # effect_test["excess"]记录 赢家组合超额收益，输家组合超额收益
        # effect_test["prob"]记录 赢家组合跑赢概率和输家组合跑输概率;【>0.5,>0.4】合格(因实际情况，跑输概率暂时不考虑)
        win_excess_return = self.effect_test[fac]["excess"][0]
        loss_total_return = l_total_return
        loss_annual_return = l_annual_return
        loss_excess_return = self.effect_test[fac]["excess"][1]
        win_prob = self.win_prob[fac]
        loss_prob = self.loss_prob[fac]
        factor_ic = fac_ic
        # 1-有效 0-无效
        is_valid = 1
        if abs(fac_ic) < self.min_corr:
            is_valid = 0
        sample_periods = self.sample_periods
        memo = ''
        sql2 = r'select * from factor_validity_info where factor_id=%s'
        args = fac
        res = self.db.selectone(sql=sql2, param=args)
        if res is not None:
            sql3 = r'delete from factor_validity_info WHERE factor_id=%s'
            args = fac
            res = self.db.delete(sql3, args)
        sql4 = r"""insert into factor_validity_info
               (factor_id,factor_name,factor_type_id,factor_type,benchmark,
               benchmark_name,benchmark_total_return,benchmark_annual_return,win_total_return,
               win_annual_return,win_excess_return,loss_total_return,loss_annual_return,
               loss_excess_return,win_prob,loss_prob,factor_ic,is_valid,sample_periods,memo) 
               values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        res = self.db.insertone(sql4, (factor_id, factor_name, factor_type_id, factor_type, benchmark,
                                       benchmark_name, benchmark_total_return, benchmark_annual_return,
                                       win_total_return, win_annual_return, win_excess_return, loss_total_return,
                                       loss_annual_return, loss_excess_return, win_prob, loss_prob, factor_ic,
                                       is_valid, sample_periods, memo))

    def init_sample_months(self):
        self.sample_months = {'01': '02', '02': '03', '03': '04', '04': '05',
                              '05': '06', '06': '07', '07': '08', '08': '09',
                              '09': '10', '10': '11', '11': '12', '12': '12'}

    def default_factors(self):
        """默认因子集"""
        # ['pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm', 'dv_ratio', 'eps', 'bps', 'roe', 'roe_yearly', 'npta', 'roa',
        #  'roa_yearly', 'roa2_yearly', 'roic', 'basic_eps_yoy', 'op_yoy', 'ebt_yoy', 'tr_yoy', 'or_yoy', 'equity_yoy',
        #  'netprofit_margin', 'grossprofit_margin', 'profit_to_gr', 'op_of_gr', 'debt_to_assets', 'total_mv', 'circ_mv',
        #  'volume', 'amount', 'current_ratio', 'quick_ratio', 'turnover_rate', 'turnover_rate_f', 'volume_ratio',
        #  'changepercent']
        # ['市盈率', '市盈率TTM', '市净率', '市销率', '市销率TTM', '股息率', '基本每股收益', '每股净资产', '净资产收益率', '年化净资产收益率', '总资产净利润', '总资产报酬率',
        #  '年化总资产净利率', '年化总资产报酬率', '投入资本回报率', '基本每股收益(eps)同比增长率', '营业利润同比增长率', '利润总额同比增长率', '营业总收入同比增长率', '营业收入同比增长率',
        #  '净资产同比增长率', '销售净利率', '销售毛利率', '净利润率', '营业利润率', '资产负债率', '总市值', '流通市值', '成交量', '成交额', '流动比率', '速动比率', '换手率',
        #  '换手率（自由流通股）', '量比', '涨跌幅']
        sql = r'select * from candidate_factors'
        res = self.db.selectall(sql=sql)
        self.factors = [item[1] for item in res]

    def draw_return_picture(self):
        for fac in self.factors:
            df = self.monthly_return[[fac]]
            plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 用来正常显示中文标签
            plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
            plt.xticks(size=12, rotation=50)  # 设置字体大小和字体倾斜度
            fig = plt.figure()
            fig.suptitle('Figure: return for %s' % fac)
            # (df.T + 1).cumprod().iloc[:, 0].plot(label='port1')
            plt.plot(np.array((df.T + 1).cumprod().iloc[:, 0]), label='port1')
            plt.plot(np.array((df.T + 1).cumprod().iloc[:, 1]), label='port2')
            # (df.T + 1).cumprod().iloc[:, 1].plot(label='port2')
            # (df.T + 1).cumprod().iloc[:, 2].plot(label='port3')
            plt.plot(np.array((df.T + 1).cumprod().iloc[:, 2]), label='port3')
            plt.plot(np.array((df.T + 1).cumprod().iloc[:, 3]), label='port4')
            # (df.T + 1).cumprod().iloc[:, 3].plot(label='port4')
            # (df.T + 1).cumprod().iloc[:, 4].plot(label='port5')
            # (df.T + 1).cumprod().iloc[:, 5].plot(label='benchmark')
            plt.plot(np.array((df.T + 1).cumprod().iloc[:, 4]), label='port5')
            plt.plot(np.array((df.T + 1).cumprod().iloc[:, 5]), label='benchmark')
            plt.xlabel('return of factor %s' % fac)
            plt.legend(loc=0)
            plt.show()
