# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging
import time
import pandas as pd
from pandas import DataFrame
from quotation.captures.tsdata_capturer import TuShareDataCapturer
import numpy as np

from util.timeUtil import get_befortoday_Ymd, get_after_today_Ymd

'''
--------------------------------------
smb_industry_map：
           --  大盘股       -- 行业 ---  base_stock_infos(DataFrame)
全部股票    ｜
           --  中小盘股     -- 行业 ---   base_stock_infos(DataFrame)
*******************************************************************************           


{
    '深':{
        行业1：base_stock_infos(DataFrame),
        行业2：base_stock_infos(DataFrame),
        ... ...
    },
    '沪':{
        行业1：base_stock_infos(DataFrame),
        行业2：base_stock_infos(DataFrame),
        ... ...
    }
}
base_stock_infos每行包括：
  1. 估值指标【市盈率、市净率、总股本、总市值、流通股本、流通市值】
  2. 财务指标【净利润、净利润增长率、营业收入、毛利率、净利率、每股现金流、每股收益、每股净资产、资产负债率、股东户数、股息率、净资产收益率、营收增长率】
  3. 技术面指标：股价、涨跌幅、涨跌停、换手率、振幅、成交量量比、主力资金、委比、成交额           
           
--------------------------------------
'''
# ----  log ------ #
log = logging.getLogger("log_quantization")
log_err = logging.getLogger("log_err")


# ----  log ------ #


# noinspection PyMethodMayBeStatic,SpellCheckingInspection,PyIncorrectDocstring
class BaseDataClean(object):
    # 上一个交易日
    pretrade_date: str = None
    # 股票池 [上市]
    stocks_pool = DataFrame()
    # 亿 [万元--->亿元]
    billion = 10000.0 / 100000000.0
    # 全部：基本面数据 交易数据 时间默认为当前交易日的上一个交易日
    base_stock_infos = None
    # 股票分类字典
    # {
    #     "小盘股":{"行业1":stockinfoDataFrame,"行业2":stockinfoDataFrame,...},
    #     "中盘股":{"行业1":stockinfoDataFrame,"行业2":stockinfoDataFrame,...},
    #     "大盘股":{"行业1":stockinfoDataFrame,"行业2":stockinfoDataFrame,...}
    # }
    smb_industry_map = dict()
    # ts code
    tscode_set = set()
    # 行业
    industry_set = set()
    # 小盘股
    small_cap_stocks = list()
    # 中盘股
    mid_cap_stocks = list()
    # 大盘股
    big_cap_stocks = list()
    labels = ['小盘股', '中盘股', '大盘股']
    # 分位数设定
    cut = [4.5, 20.0]
    # 行情获取
    tsdatacapture: TuShareDataCapturer = TuShareDataCapturer()
    instance = None

    # 保证单例
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self) -> object:
        # 初始化 股票池 [上市] stocks_pool
        # self.init_stocks_pool()
        # 初始化 tscode_set
        self.init_tscode_set()
        '''
        初始化 industry_set small_cap_stocks mid_cap_stocks big_cap_stocks ---- > smb_industry_map
        将上市的股票 按照大小盘、行业进行分类存储
        {
            "小盘股": {"行业1": stockinfoDataFrame, "行业2": stockinfoDataFrame, ...},
            "中盘股": {"行业1": stockinfoDataFrame, "行业2": stockinfoDataFrame, ...},
            "大盘股": {"行业1": stockinfoDataFrame, "行业2": stockinfoDataFrame, ...}
        }
        '''
        self.init_smb_industry_map()
        log.info("BaseDataClean load done.")

    @classmethod
    def init_base_stock_infos(cls):
        """
        init base_stock_infos
        - 选股范围：市场【沪深】、行业 --- stocks_pool  done
        - 基本面：
          1. 估值指标【市盈率、市盈率TTM、市净率、市销率、市销率TTM、总股本、总市值、流通股本、流通市值】  -- basics_data  done
          2. 财务指标【股息率、股息率TTM、
                    净利润、净利润增长率、营业收入、毛利率、净利率、每股现金流、每股收益、
                    每股净资产、资产负债率、股东户数、净资产收益率、营收增长率】
        - 技术面：股价、涨跌幅、换手率、振幅、成交额、
                涨跌停、成交量量比、委比 【】
        """
        # 市场、行业数据
        ex_indu_data = None
        # 全部股票每日重要的基本面指标
        basics_data = None
        # 交易数据 一次性获取最近一个日交易日所有股票的交易数据
        trade_data = None

        need_col = ['ts_code', 'symbol', 'industry', 'exchange',
                    'pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm', 'total_share', 'float_share', 'total_mv', 'circ_mv',
                    'dv_ratio', 'dv_ttm', 'changepercent', 'trade', 'volume', 'turnoverratio', 'amount'
                    ]
        rename_col = ['TS股票代码', '股票代码', '行业', '交易所',
                      '市盈率', '市盈率TTM', '市净率', '市销率', '市销率TTM', '总股本', '流通股本', '总市值', '流通市值',
                      '股息率', '股息率TTM', '涨跌幅', '现价', '成交量', '换手率', '成交额'
                      ]
        rename_dict = dict(zip(need_col, rename_col))
        try:
            # sw_data=BaseDataClean.tsdatacapture.get_sw_daily(trade_date=BaseDataClean.get_pretrade_date())
            # print(sw_data.head(1).to_dict())
            cls.init_stocks_pool()
            # 市场、行业数据
            # ei_col = ['ts_code', 'symbol', 'industry', 'exchange']
            ex_indu_data = BaseDataClean.stocks_pool
            # add exchange  df.insert(loc=len(df.columns), column='player', value=player_vals)
            exchange_data = ex_indu_data['ts_code'].tolist()
            exchange_data = [x.split('.')[1] for x in exchange_data]
            exchange_data=pd.Series(exchange_data)
            print(exchange_data)
            ex_indu_data.insert(loc=len(ex_indu_data.columns), column='exchange', value=exchange_data)
            # 全部股票每日重要的基本面指标
            b_col = ['ts_code', 'pe', 'pe_ttm', 'pb', 'ps', 'ps_ttm', 'total_share', 'float_share', 'total_mv',
                     'circ_mv', 'dv_ratio', 'dv_ttm']
            basics_data: DataFrame = BaseDataClean.tsdatacapture.get_daily_basic(
                trade_date=BaseDataClean.get_pretrade_date())[b_col]
            # print(basics_data.head(1).to_dict())
            BaseDataClean.base_stock_infos = pd.merge(left=ex_indu_data, right=basics_data, on='ts_code')

            # 股价1、涨跌幅1、成交额1、换手率1、  振幅、成交量量比、主力资金、委比、涨跌停
            # 近一个日交易日所有股票的交易数据
            # 代码,涨跌幅,现价,成交量,换手率,成交额,
            t_col = ['code', 'changepercent', 'trade', 'volume', 'turnoverratio', 'amount']
            trade_data: DataFrame = BaseDataClean.tsdatacapture.get_today_all()[t_col]
            trade_data.rename(columns={'code': 'symbol'}, inplace=True)
            BaseDataClean.base_stock_infos = pd.merge(left=BaseDataClean.base_stock_infos, right=trade_data,
                                                      on='symbol')
            # print(trade_data.head(1).to_dict())

            # TS股票代码 公告日期 报告期 基本每股收益  流动比率  速动比率  每股净资产 销售净利率  销售毛利率
            # 营业净利率  净利润率  净资产收益率 总资产报酬率 总资产净利润  投入资本回报率
            # 年化净资产收益率 年化总资产报酬率 资产负债率 营业利润同比增长率(%) 利润总额同比增长率(%)
            # 营业总收入同比增长率(%) 营业收入同比增长率(%) 净资产同比增长率 更新标识
            f_col = ['ts_code', 'ann_date', 'end_date', 'eps', 'current_ratio', 'quick_ratio', 'bps',
                     'netprofit_margin', 'grossprofit_margin', 'profit_to_gr', 'op_of_gr', 'roe',
                     'roa', 'npta', 'roic', 'roe_yearly', 'roa2_yearly', 'debt_to_assets', 'op_yoy',
                     'ebt_yoy', 'tr_yoy', 'or_yoy', 'equity_yoy', 'update_flag']
            fina_indicator: DataFrame = BaseDataClean.tsdatacapture.get_fina_indicator()
            if fina_indicator is not None:
                fina_indicator = fina_indicator[f_col]
                fina_indicator.drop_duplicates(subset=['ts_code'], keep='first', inplace=True)
                BaseDataClean.base_stock_infos = pd.merge(left=BaseDataClean.base_stock_infos, right=fina_indicator,
                                                          on='ts_code')

                print(BaseDataClean.base_stock_infos)
                print(BaseDataClean.base_stock_infos.head(1).to_dict())
            pass
        except Exception as e:
            log_err.error("BaseDataClean.base_stock_infos init Failed!", e)
        pass

    def init_tscode_set(self):
        try:
            for idx, sata in BaseDataClean.stocks_pool.iterrows():
                BaseDataClean.tscode_set.add(sata['ts_code'])
            log.info("BaseDataClean.tscode_set init sucess.")
        except Exception as e:
            log_err.error("BaseDataClean.tscode_set init Failed! ", e)
            raise Exception("BaseDataClean.tscode_set init Failed! %s" % e)

    @classmethod
    def init_stocks_pool(cls):
        try:
            #
            cls.stocks_pool = BaseDataClean.tsdatacapture.get_stock_list()
            log.info("BaseDataClean.stocks_pool init sucess.")
        except Exception as e:
            log_err.error("BaseDataClean.stocks_pool init Failed! ", e)
            raise Exception("BaseDataClean.stocks_pool init Failed! %s" % e)

    def init_smb_industry_map(self):
        """
        计算 smb_industry_map
        {
             "小盘股":{"行业1":stockinfoDataFrame,"行业2":stockinfoDataFrame,...},
             "中盘股":{"行业1":stockinfoDataFrame,"行业2":stockinfoDataFrame,...},
             "大盘股":{"行业1":stockinfoDataFrame,"行业2":stockinfoDataFrame,...}
        }
        """
        BaseDataClean.smb_industry_map = {
            '小盘股': {}, '中盘股': {}, '大盘股': {}
        }
        # 获取流通市值 float_share、行业 industry
        dfall = None
        try:
            dfall = BaseDataClean.tsdatacapture.get_bak_basic()
        except Exception as e:
            log_err.error("BaseDataClean.tsdatacapture.get_bak_basic Failed! ", e)
            raise Exception("BaseDataClean.tsdatacapture.get_bak_basic Failed! %s" % e)
        for idx, stkdata in dfall.iterrows():
            ts_code = stkdata['ts_code']
            BaseDataClean.tscode_set.discard(ts_code)
        for tcod in BaseDataClean.tscode_set:
            df = BaseDataClean.tsdatacapture.get_bak_basic(ts_code=tcod)
            dfall = dfall.append(df, ignore_index=True)
        # print("BaseDataClean\r\n"+dfall.head(5))

        # 此次划分标准：分析 流通股本的中位数、75%分位数、90%分位数
        # 中位数以下：小盘股
        # 90%分位数以上：大盘股
        data_max, data_min, valuation_low, valuation_mid, valuation_high = self.get_data_percentile(
            np.array(dfall.iloc[:].loc[:, 'float_share']).tolist(), 50, 75, 90)
        for idx, stkdata in dfall.iterrows():
            float_mv = stkdata["float_share"]
            ele_industry = stkdata["industry"]
            BaseDataClean.industry_set.add(stkdata["industry"])
            if float_mv <= valuation_low:
                BaseDataClean.small_cap_stocks.append(stkdata)
                if BaseDataClean.smb_industry_map['小盘股'].get(ele_industry) is None:
                    BaseDataClean.smb_industry_map['小盘股'][ele_industry] = DataFrame()
                BaseDataClean.smb_industry_map['小盘股'][ele_industry] = BaseDataClean.smb_industry_map['小盘股'][
                    ele_industry].append(stkdata, ignore_index=True)
                # BaseDataClean.smb_industry_map['小盘股'][ele_industry].append(stkdata)
            elif float_mv >= valuation_high:
                BaseDataClean.big_cap_stocks.append(stkdata)
                if BaseDataClean.smb_industry_map['大盘股'].get(ele_industry) is None:
                    BaseDataClean.smb_industry_map['大盘股'][ele_industry] = DataFrame()
                # BaseDataClean.smb_industry_map['大盘股'][ele_industry].append(stkdata)
                BaseDataClean.smb_industry_map['大盘股'][ele_industry] = BaseDataClean.smb_industry_map['大盘股'][
                    ele_industry].append(stkdata, ignore_index=True)

            else:
                BaseDataClean.mid_cap_stocks.append(stkdata)
                if BaseDataClean.smb_industry_map['中盘股'].get(ele_industry) is None:
                    BaseDataClean.smb_industry_map['中盘股'][ele_industry] = DataFrame()
                # BaseDataClean.smb_industry_map['中盘股'][ele_industry].append(stkdata)
                BaseDataClean.smb_industry_map['中盘股'][ele_industry] = BaseDataClean.smb_industry_map['中盘股'][
                    ele_industry].append(stkdata, ignore_index=True)
        # %s" % e
        log.info("大盘股数量：", len(BaseDataClean.big_cap_stocks), "中盘股数量：", len(BaseDataClean.mid_cap_stocks), "小盘股数量：",
                 len(BaseDataClean.small_cap_stocks))
        log.info("BaseDataClean.smb_industry_map init sucess.")

    def get_data_percentile(self, data: list, v_low=50.0, v_mid=83.83, v_high=94.22) -> tuple:
        """
        获取 data 最大值 最小值  高、中、低分位数
        :param data:
        :return:
        """
        if data is None or len(data) < 1:
            log_err.error("BaseDataClean.get_data_percentile 参数data异常!")
            raise Exception("BaseDataClean.get_data_percentile 参数data异常:", data)

        data_max = max(data)
        data_min = min(data)
        valuation_high = np.percentile(data, v_high)
        valuation_mid = np.percentile(data, v_mid)
        valuation_low = np.percentile(data, v_low)
        return data_max, data_min, valuation_low, valuation_mid, valuation_high

    @classmethod
    def get_pretrade_date(cls) -> str:
        """获取上一个交易日"""
        start_date = get_befortoday_Ymd(7)
        end_date = get_after_today_Ymd(0)
        trade_cal = BaseDataClean.tsdatacapture.get_trade_cal(start_date=start_date, end_date=end_date)
        # print(trade_cal.head(3))
        if trade_cal is not None:
            BaseDataClean.pretrade_date = trade_cal['pretrade_date'].loc[0]
        log.info("pretrade_date is %s." % BaseDataClean.pretrade_date)
        return str(BaseDataClean.pretrade_date)
