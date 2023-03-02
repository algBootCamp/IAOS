# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging
import logging.config

from pandas import DataFrame
from quotation.captures.tsdata_capturer import TuShareDataCapturer
import numpy as np

'''
选股是一个系统的思维过程，需要回答多个问题：
如选择什么样的股？为什么买入这只股？上涨空间如何？持股时间多长？出现错误的概率是多少？
--------------------------------------
选股思路：
选股涉及两个方面：
一是公司分析，包括财务状况、发展潜力和成长性等，这方面是俗称的基本面分析，是股票投资者的基本素质要求；
二是股票分析。 股票分析主要回答三个问题：
（1）如何判断一只股票有投资价值？
（2）如何从股票池中选出符合自己认为有价值的股票？
（3）选出合适的股票后如何构建投资组合并动态调整？
总体思维：多层次多角度分析
（1）多角度保证在市场大方向上看对的正确率尽可能增加，多层次可以和多角度相互验证，获取超额收益。
（2）通过自上而下（宏观-产业-公司）的分析框架确定投资方向，选择符合投资方向的最优标的。
--------------------------------------
大盘股vs小盘股
为什么要划分大盘股和中小盘股呢？换句话，大盘股和小盘股有什么明显的区别吗？
一般而言，相同业绩的个股，小盘股的市盈率比中盘股高，中盘股要比大盘股高。
特别在市场疲软时，小盘股机会较多。在牛市时大盘股和中盘股较适合大资金的进出，因此盘子大的个股比较看好。
由于流通盘大，对指数影响大，往往成为市场调控指数的工具。投资者选择个股，一般熊市应选小盘股和中小盘股，
牛市应选大盘股和中大盘股。
如何划分？

市场上传统划分方法是根据流通股本的大小：
一般流通股本超过 10 亿股为大盘股，
流通股本小于 5 亿股为小盘股，
流通股本 5 亿- 10 亿的属于中盘股。

如果以市值衡量，
总市值大于 1000 亿的属于超大盘股，总市值大于 500 亿以上的属于大盘股，
总市值小于200亿的属于小盘股，
处于 200 亿-500 亿总市值的股票，属于中盘股。
实际上关于大盘股和中小盘股的划分并没有统一的标准。

大盘股和小盘股的区别并不是固定的，随着上市公司的增多，以及A股市场总市值的不断变化，大小盘股的划分标准也应该是动态变化的。

此次划分标准：分析 流通股本的中位数、75%分位数、90%分位数
4.043335300000001 9.524347610000001 22.142985079000017          
中位数以下：小盘股
90%分位数以上：大盘股

--------------------------------------
实现思路：
使用tushare包获取基本面和交易数据，使用Pandas和Matplotlib对数据特征进行描述性统计和可视化分析；
根据股票财务和行情指标进行排序，通过设置参数和过滤值筛选股票。
具体指标包括 动态市盈率、市净率、流通股本、总市值、每股公积金、每股收益、收入同比、利润同比、毛利率、净利润率等。
--------------------------------------

           --  大盘股       -- 行业 ---  指标排序
全部股票    ｜
           --  中小盘股     -- 行业 ---   指标排序
           
--------------------------------------

'''
# ----  log ------ #
log = logging.getLogger("log_quantization")
log_err = logging.getLogger("log_err")


# ----  log ------ #

# noinspection PyMethodMayBeStatic,SpellCheckingInspection,PyIncorrectDocstring
class StockPick01(object):
    # 股票池 [上市]
    stocks_pool = DataFrame()
    # 亿 [万元--->亿元]
    billion = 10000.0 / 100000000.0
    # 基本面数据
    basics_data = None
    # 交易数据
    trade_data = None
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
    basicindexdata: DataFrame = tsdatacapture.get_daily_basic()
    instance = None

    # 保证单例
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self) -> object:
        # 初始化 股票池 [上市] stocks_pool
        self.init_stocks_pool()
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
        log.info("StockPick01 load done.")

    def init_tscode_set(self):
        try:
            for idx, sata in StockPick01.stocks_pool.iterrows():
                StockPick01.tscode_set.add(sata['ts_code'])
            log.info("StockPick01.tscode_set init sucess.")
        except Exception as e:
            log_err.error("StockPick01.tscode_set init Failed! %s" % e)
            raise Exception("StockPick01.tscode_set init Failed! %s" % e)

    def init_stocks_pool(self):
        try:
            StockPick01.stocks_pool = StockPick01.stocks_pool.append(StockPick01.tsdatacapture.get_stock_list())
            log.info("StockPick01.stocks_pool init sucess.")
        except Exception as e:
            log_err.error("StockPick01.stocks_pool init Failed! %s" % e)
            raise Exception("StockPick01.stocks_pool init Failed! %s" % e)

    def init_smb_industry_map(self):
        """
        计算 smb_industry_map
        {
             "小盘股":{"行业1":stockinfoDataFrame,"行业2":stockinfoDataFrame,...},
             "中盘股":{"行业1":stockinfoDataFrame,"行业2":stockinfoDataFrame,...},
             "大盘股":{"行业1":stockinfoDataFrame,"行业2":stockinfoDataFrame,...}
        }
        """
        StockPick01.smb_industry_map = {
            '小盘股': {}, '中盘股': {}, '大盘股': {}
        }
        # 获取流通市值 float_share、行业 industry
        dfall = None
        try:
            dfall = StockPick01.tsdatacapture.get_bak_basic()
        except Exception as e:
            log_err.error("StockPick01.tsdatacapture.get_bak_basic Failed! %s" % e)
            raise Exception("StockPick01.tsdatacapture.get_bak_basic Failed! %s" % e)
        for idx, stkdata in dfall.iterrows():
            ts_code = stkdata['ts_code']
            StockPick01.tscode_set.discard(ts_code)
        # print("StockPick01  \r\n"+StockPick01.tscode_set)
        for tcod in StockPick01.tscode_set:
            df = StockPick01.tsdatacapture.get_bak_basic(ts_code=tcod)
            dfall = dfall.append(df, ignore_index=True)
        # print("StockPick01\r\n"+dfall.head(5))

        # 此次划分标准：分析 流通股本的中位数、75%分位数、90%分位数
        # 中位数以下：小盘股
        # 90%分位数以上：大盘股
        data_max, data_min, valuation_low, valuation_mid, valuation_high = self.get_data_percentile(
            np.array(dfall.iloc[:].loc[:, 'float_share']).tolist(), 50, 75, 90)
        for idx, stkdata in dfall.iterrows():
            float_mv = stkdata["float_share"]
            ele_industry = stkdata["industry"]
            StockPick01.industry_set.add(stkdata["industry"])
            if float_mv <= valuation_low:
                StockPick01.small_cap_stocks.append(stkdata)
                if StockPick01.smb_industry_map['小盘股'].get(ele_industry) is None:
                    StockPick01.smb_industry_map['小盘股'][ele_industry] = DataFrame()
                StockPick01.smb_industry_map['小盘股'][ele_industry] = StockPick01.smb_industry_map['小盘股'][
                    ele_industry].append(stkdata, ignore_index=True)
                # StockPick01.smb_industry_map['小盘股'][ele_industry].append(stkdata)
            elif float_mv >= valuation_high:
                StockPick01.big_cap_stocks.append(stkdata)
                if StockPick01.smb_industry_map['大盘股'].get(ele_industry) is None:
                    StockPick01.smb_industry_map['大盘股'][ele_industry] = DataFrame()
                # StockPick01.smb_industry_map['大盘股'][ele_industry].append(stkdata)
                StockPick01.smb_industry_map['大盘股'][ele_industry] = StockPick01.smb_industry_map['大盘股'][
                    ele_industry].append(stkdata, ignore_index=True)

            else:
                StockPick01.mid_cap_stocks.append(stkdata)
                if StockPick01.smb_industry_map['中盘股'].get(ele_industry) is None:
                    StockPick01.smb_industry_map['中盘股'][ele_industry] = DataFrame()
                # StockPick01.smb_industry_map['中盘股'][ele_industry].append(stkdata)
                StockPick01.smb_industry_map['中盘股'][ele_industry] = StockPick01.smb_industry_map['中盘股'][
                    ele_industry].append(stkdata, ignore_index=True)
        # %s" % e
        log.info("大盘股数量：{} 中盘股数量：{} 小盘股数量：{}".format(len(StockPick01.big_cap_stocks), len(StockPick01.mid_cap_stocks),
                                                     len(StockPick01.small_cap_stocks)))
        log.info("StockPick01.smb_industry_map init sucess.")

    def get_data_percentile(self, data: list, v_low=50.0, v_mid=83.83, v_high=94.22) -> tuple:
        """
        获取 data 最大值 最小值  高、中、低分位数
        :param data:
        :return:
        """
        if data is None or len(data) < 1:
            log_err.error("StockPick01.get_data_percentile 参数data异常!")
            raise Exception("StockPick01.get_data_percentile 参数data异常:%s" % data)

        data_max = max(data)
        data_min = min(data)
        valuation_high = np.percentile(data, v_high)
        valuation_mid = np.percentile(data, v_mid)
        valuation_low = np.percentile(data, v_low)
        return data_max, data_min, valuation_low, valuation_mid, valuation_high

#
# def get_data():
#     global basics_data
#     global trade_data
#     basics_data = tsdatacapture.get_bak_basic(trade_date="20220909")
#     # 时间默认为当前交易日的上一个交易日
#     trade_data = tsdatacapture.get_today_all()
#     print(basics_data.head(3))
#     # print(trade_data.head(3))
#     # 基本面数据清洗
#     b_col = ['ts_code', 'name', 'float_share', 'pe', 'pb', 'eps',
#              'reserved_pershare', 'rev_yoy', 'profit_yoy', 'gpr', 'npr']
#     b_colcn = ['TS股票代码', '简称', '流通股', '市盈率', '市净率',
#                '每股收益', '每股公积', '收入同比', '利润同比', '毛利率', '净利率']
#     d = dict(zip(b_col, b_colcn))
#     b_data = basics_data.iloc[:].loc[:, b_col]
#     b_data.rename(columns=d, inplace=True)
#     print(b_data.head())
#
#     # 交易数据清洗
#     ##当前股价,如果停牌则设置当前价格为上一个交易日股价
#     trade_data['trade'] = trade_data.apply(lambda x: x.settlement if x.trade == 0 else x.trade, axis=1)
#     # 选取股票代码,名称,当前价格,总市值,流通市值
#     t_data = trade_data.loc[:, ['ts_code', 'trade', 'mktcap', 'nmc', 'volume', 'turnoverratio']]
#     # 设置行情数据code为index列
#     t_data = t_data.set_index('code')
#     t_data.rename(columns={'code': '股票代码', 'trade': '收盘价', 'mktcap': '总市值', 'nmc': '流通市值',
#                            'volume': '成交量', 'turnoverratio': '换手率'}, inplace=True)
#     # 将总市值和流通值换成亿元单位
#     t_data['总市值'] = t_data['总市值'] * billion
#     t_data['流通市值'] = t_data['流通市值'] * billion
#     print(t_data.head())
#
#     # 合并两个数据表
#     com_data = b_data.merge(t_data, left_index=True, right_index=True)
#     print(com_data.head())
#
#     # 数据描述性统计
#     print(com_data.describe().round(2))
#
#     # 调用函数df_cut,增加新列
#     # data_new=data.loc[:,['简称','收盘价','流通股','市盈率','每股收益','净利率','收入同比','利润同比']]
#     # data_new['股票类型'] = df_cut(data['流通股'], cut, labels)
#     # #查看标签列，取值范围前面加上了序号，是便于后面生成表格时按顺序排列
#     # data_new.head()
#
#
# def get_industry_info():
#     """
#     股票行业划分
#     """
#     df = tsdatacapture.get_stock_list()
#     for ele in df["industry"]:
#         industry_set.add(ele)
#     for ind in industry_set:
#         industry_map[ind] = list()
#     for index, row in df.iterrows():
#         # print(index, type(row), row['industry'], row['ts_code'])
#         industry_map[row['industry']].append(row['ts_code'])
#     print(df.head(3))
#     print(industry_map)
#
#
# # get_industry_info()
# # partition_cap()
# get_data()
