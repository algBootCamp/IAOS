# -*- coding: utf-8 -*-
__author__ = 'carl'

import warnings

import tushare as ts
from pandas import DataFrame

from conf.globalcfg import GlobalCfg
from util.decorator_util import retry

warnings.filterwarnings("ignore")
'''
tushare数据获取器 当为单例
'''


# noinspection SpellCheckingInspection,PyMethodMayBeStatic,PyTypeChecker
class TuShareDataCapturer(object):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self) -> object:
        cfg = GlobalCfg()
        self.ts_info = cfg.get_ts_info()
        ts.set_token(self.get_token())
        self.pro = ts.pro_api(timeout=60)

    def get_token(self) -> str:
        return self.ts_info["token"]

    '''----------------------以下：沪深股票数据----------------------'''
    '''----------------------以下：基础数据----------------------'''

    @retry(max_retry=5, time_interval=3)
    def get_stock_list(self) -> DataFrame:
        """
        查询当前所有正常上市交易的股票列表
        return:
        --------------------------
        ts_code	str	Y	TS代码
        symbol	str	Y	股票代码
        name	str	Y	股票名称
        area	str	Y	地域
        industry	str	Y	所属行业
        fullname	str	N	股票全称
        enname	str	N	英文全称
        cnspell	str	N	拼音缩写
        market	str	Y	市场类型（主板/创业板/科创板/CDR）
        exchange	str	N	交易所代码
        curr_type	str	N	交易货币
        list_status	str	N	上市状态 L上市 D退市 P暂停上市
        list_date	str	Y	上市日期
        delist_date	str	N	退市日期
        is_hs	str	N	是否沪深港通标的，N否 H沪股通 S深股通
        """
        df = self.pro.stock_basic(list_status='L')
        return df

    @retry(max_retry=3, time_interval=2)
    def get_bak_basic(self, ts_code: str = None, trade_date: str = None) -> DataFrame:
        """
        获取备用基础列表，数据从2016年开始
        trade_date	        str	N	交易日期
        ts_code	            str	N	股票代码
        ___________________________
        return
        trade_date	        str	Y	交易日期
        ts_code	            str	Y	TS股票代码
        name	            str	Y	股票名称
        industry	        str	Y	行业
        area	            str	Y	地域
        pe	                float	Y	市盈率（动）
        float_share	        float	Y	流通股本（亿）
        total_share	        float	Y	总股本（亿）
        total_assets	    float	Y	总资产（亿）
        liquid_assets	    float	Y	流动资产（亿）
        fixed_assets	    float	Y	固定资产（亿）
        reserved	        float	Y	公积金
        reserved_pershare	float	Y	每股公积金
        eps	                float	Y	每股收益
        bvps	            float	Y	每股净资产
        pb	                float	Y	市净率
        list_date	        str	Y	上市日期
        undp	            float	Y	未分配利润
        per_undp	        float	Y	每股未分配利润
        rev_yoy	            float	Y	收入同比（%）
        profit_yoy      	float	Y	利润同比（%）
        gpr	                float	        Y	毛利率（%）
        npr	                float	        Y	净利润率（%）
        holder_num	        int	Y	股东人数
        """
        df = self.pro.bak_basic(ts_code=ts_code, trade_date=trade_date)
        return df

    @retry(max_retry=3, time_interval=1)
    def get_trade_cal(self, exchange: str = 'SSE', start_date: str = '20220101', end_date: str = '20990101',
                      is_open: str = '1') -> DataFrame:
        """获取各大交易所交易日历数据 交易所 SSE上交所 SZSE深交所"""
        df = self.pro.trade_cal(exchange=exchange, start_date=start_date, end_date=end_date, is_open=is_open)
        return df

    @retry(max_retry=3, time_interval=1)
    def get_stock_company(self, ts_code: str = None, exchange: str = None) -> DataFrame:
        """上市公司基本信息 获取上市公司基础信息，单次提取4500条，可以根据交易所分批提取"""
        df = self.pro.stock_company(exchange=exchange, ts_code=ts_code,
                                    fields='ts_code,chairman,manager,secretary,reg_capital,setup_date,province')
        return df

    @retry(max_retry=3, time_interval=1)
    def get_stk_rewards(self, ts_code: str = None, end_date: str = None) -> DataFrame:
        """管理层薪酬和持股 end_date:报告期  ts_code: TS股票代码，支持单个或多个代码输入"""
        df = self.pro.stk_rewards(ts_code=ts_code, end_date=end_date)
        return df

    @retry(max_retry=3, time_interval=1)
    def get_new_share(self, start_date: str = None, end_date: str = None) -> DataFrame:
        """
        获取新股上市列表数据 IPO新股列表
        start_date:上网发行开始日期
        end_date:上网发行结束日期 限量：单次最大2000条
        s_code股票代码（支持多个股票同时提取，逗号分隔）
        """
        df = self.pro.new_share(start_date=start_date, end_date=end_date)
        return df

    '''----------------------以下：行情数据----------------------'''

    @retry(max_retry=3, time_interval=2)
    def get_daily(self, ts_code: str = None, trade_date: str = None, start_date: str = None,
                  end_date: str = None) -> DataFrame:
        """
        A股日线行情 (未复权行情) 数据说明：交易日每天15点～16点之间入库。本接口是 未复权行情，停牌期间不提供数据
        """
        df = self.pro.daily(ts_code=ts_code, trade_date=trade_date, start_date=start_date, end_date=end_date)
        return df

    @retry(max_retry=3, time_interval=2)
    def get_weekly(self, ts_code: str = None, trade_date: str = None, start_date: str = None,
                   end_date: str = None) -> DataFrame:
        """周线行情 获取A股周线行情(未复权行情)"""
        df = self.pro.weekly(ts_code=ts_code, trade_date=trade_date, start_date=start_date, end_date=end_date)
        return df

    @retry(max_retry=3, time_interval=1)
    def get_monthly(self, ts_code: str = None, trade_date: str = None, start_date: str = None,
                    end_date: str = None) -> DataFrame:
        """获取A股月线数据(未复权行情)"""
        df = self.pro.monthly(ts_code=ts_code, trade_date=trade_date, start_date=start_date, end_date=end_date)
        return df

    # @retry_for_none
    @retry(max_retry=3, time_interval=5)
    def get_adj_factor(self, ts_code: str = '', trade_date: str = None, start_date: str = None,
                       end_date: str = None):
        """
        输入参数
        名称	类型	必选	描述
        ts_code	str	N	股票代码
        trade_date	str	N	交易日期(YYYYMMDD，下同)
        start_date	str	N	开始日期
        end_date	str	N	结束日期
        注：日期都填YYYYMMDD格式，比如20181010

        输出参数
        名称	类型	描述
        ts_code	str	股票代码
        trade_date	str	交易日期
        adj_factor	float	复权因子
        """
        df = self.pro.adj_factor(ts_code=ts_code, trade_date=trade_date, start_date=start_date, end_date=end_date)
        return df

    @retry(max_retry=3, time_interval=5)
    def get_pro_bar(self, ts_code='', start_date='', end_date='', freq='D', asset='E',
                    adj=None, ma=[], factors=None, adjfactor=False,
                    offset=None, limit=None, contract_type='') -> DataFrame:
        """
        通用行情接口 根据入参，可以获取 未复权、前、后复权行情(只针对股票,即asset=E)
        入参说明：
        ts_code	    str	    Y	证券代码，不支持多值输入，多值输入获取结果会有重复记录
        api	        str	    N	pro版api对象，如果初始化了set_token，此参数可以不需要
        start_date	str	    N	开始日期 (日线格式：YYYYMMDD，提取分钟数据请用2019-09-01 09:00:00这种格式)
        end_date	str	    N	结束日期 (日线格式：YYYYMMDD)
        asset	    str	    N	资产类别：E股票 I沪深指数 C数字货币 FT期货 FD基金 O期权 CB可转债（v1.2.39），默认E
        adj	        str	    N	复权类型(只针对股票)：None未复权 qfq前复权 hfq后复权 , 默认None，目前只支持日线复权，同时复权机制是根据设定的end_date参数动态复权，采用分红再投模式。
        freq	    str	    N	数据频度 ：支持分钟(min)/日(D)/周(W)/月(M)K线，其中1min表示1分钟（类推1/5/15/30/60分钟） ，默认D。对于分钟数据有600积分用户可以试用（请求2次）。
        ma	        list	N	均线，支持任意合理int数值。注：均线是动态计算，要设置一定时间范围才能获得相应的均线，比如5日均线，开始和结束日期参数跨度必须要超过5日。目前只支持单一个股票提取均线，即需要输入ts_code参数。e.g: ma_5表示5日均价，ma_v_5表示5日均量
        factors	    list	N	股票因子（asset='E'有效）支持 tor换手率 vr量比
        adjfactor	str	    N	复权因子，在复权数据时，如果此参数为True，返回的数据中则带复权因子，默认为False。 该功能从1.2.33版本开始生效

        Return
        ----------
        DataFrame
            code:代码
            open：开盘close/high/low/vol成交量/amount成交额/maN均价/vr量比/tor换手率

                 期货(asset='FT')
            code/open/close/high/low/avg_price：均价  position：持仓量  vol：成交总量
        """
        df = ts.pro_bar(ts_code=ts_code, freq=freq, adj=adj, asset=asset, ma=ma,
                        factors=factors, adjfactor=adjfactor, start_date=start_date, end_date=end_date, offset=offset,
                        limit=limit, contract_type=contract_type)

        return df

    @retry(max_retry=5, time_interval=3)
    def get_daily_basic(self, ts_code: str = '', trade_date: str = None,
                        start_date: str = None, end_date: str = None) -> DataFrame:
        """
        获取全部股票每日重要的基本面指标
        ts_code	    str	Y	股票代码（二选一） 如果 '' 则全部
        trade_date	str	N	交易日期 （二选一）
        start_date	str	N	开始日期(YYYYMMDD)
        end_date	str	N	结束日期(YYYYMMDD)
        __________________________________________________
        return
        ts_code	        str	TS股票代码
        trade_date	    str	交易日期
        close	        float	当日收盘价
        turnover_rate	float	换手率（%）
        turnover_rate_f	float	换手率（自由流通股）
        volume_ratio	float	量比
        pe	            float	市盈率（总市值/净利润， 亏损的PE为空）
        pe_ttm	        float	市盈率（TTM，亏损的PE为空）
        pb	            float	市净率（总市值/净资产）
        ps	            float	市销率
        ps_ttm      	float	市销率（TTM）
        dv_ratio       	float	股息率 （%）
        dv_ttm	        float	股息率（TTM）（%）
        total_share	    float	总股本 （万股）
        float_share	    float	流通股本 （万股）
        free_share	    float	自由流通股本 （万）
        total_mv	    float	总市值 （万元）
        circ_mv	        float	流通市值（万元）
        """
        df = self.pro.daily_basic(ts_code=ts_code, trade_date=trade_date, start_date=start_date, end_date=end_date)
        return df

    @retry(max_retry=3, time_interval=2)
    def get_bak_daily(self, ts_code: str = None, trade_date: str = None, start_date: str = None, end_date: str = None,
                      offset: str = None, limit: str = None, fields: str = None) -> DataFrame:
        '''
        描述：获取备用行情，包括特定的行情指标
        限量：单次最大5000行数据，可以根据日期参数循环获取，正式权限需要5000积分。
        ______
        输入参数
        名称	类型	必选	描述
        ts_code	str	N	股票代码
        trade_date	str	N	交易日期
        start_date	str	N	开始日期
        end_date	str	N	结束日期
        offset	str	N	开始行数
        limit	str	N	最大行数

        输出参数
        名称	类型	默认显示	描述
        ts_code	str	Y	股票代码
        trade_date	str	Y	交易日期
        name	str	Y	股票名称
        pct_change	float	Y	涨跌幅
        close	float	Y	收盘价
        change	float	Y	涨跌额
        open	float	Y	开盘价
        high	float	Y	最高价
        low	float	Y	最低价
        pre_close	float	Y	昨收价
        vol_ratio	float	Y	量比
        turn_over	float	Y	换手率
        swing	float	Y	振幅
        vol	float	Y	成交量
        amount	float	Y	成交额
        selling	float	Y	内盘（主动卖，手）
        buying	float	Y	外盘（主动买， 手）
        total_share	float	Y	总股本(亿)
        float_share	float	Y	流通股本(亿)
        pe	float	Y	市盈(动)
        industry	str	Y	所属行业
        area	str	Y	所属地域
        float_mv	float	Y	流通市值
        total_mv	float	Y	总市值
        avg_price	float	Y	平均价
        strength	float	Y	强弱度(%)
        activity	float	Y	活跃度(%)
        avg_turnover	float	Y	笔换手
        attack	float	Y	攻击波(%)
        interval_3	float	Y	近3月涨幅
        interval_6	float	Y	近6月涨幅
        '''
        df = self.pro.bak_daily(ts_code=ts_code, trade_date=trade_date, start_date=start_date, end_date=end_date,
                                offset=offset, limit=limit, fields=fields)
        return df

    @retry(max_retry=5, time_interval=3)
    def get_today_all(self) -> DataFrame:
        """
            一次性获取最近一个日交易日所有股票的交易数据
        return
        -------
          DataFrame
               属性：代码，名称，涨跌幅，现价，开盘价，最高价，最低价，最日收盘价，成交量，换手率，成交额，市盈率，市净率，总市值，流通市值
        """

        df = ts.get_today_all()
        return df

    @retry(max_retry=3, time_interval=2)
    def get_k_data(self, code=None, start='', end='',
                   ktype='D', autype='qfq',
                   index=False,
                   retry_count=3,
                   pause=0.001) -> DataFrame:
        """
        获取k线数据 [本接口即将停止更新可使用 get_pro_bar]
        ---------
        Parameters:
          code:string
                      股票代码 e.g. 600848
          start:string
                      开始日期 format：YYYY-MM-DD 为空时取上市首日
          end:string
                      结束日期 format：YYYY-MM-DD 为空时取最近一个交易日
          autype:string
                      复权类型，qfq-前复权 hfq-后复权 None-不复权，默认为qfq
          ktype：string
                      数据类型，D=日k线 W=周 M=月 5=5分钟 15=15分钟 30=30分钟 60=60分钟，默认为D
          retry_count : int, 默认 3
                     如遇网络等问题重复执行的次数
          pause : int, 默认 0
                    重复请求数据过程中暂停的秒数，防止请求间隔时间太短出现的问题
        return
        -------
          DataFrame
              date 交易日期 (index)
              open 开盘价
              high  最高价
              close 收盘价
              low 最低价
              volume 成交量
              amount 成交额
              turnoverratio 换手率
              code 股票代码
        """
        df = ts.get_k_data(code=code, start=start, end=end,
                           ktype=ktype, autype=autype,
                           index=index,
                           retry_count=retry_count,
                           pause=pause)
        return df

    @retry(max_retry=3, time_interval=2)
    def get_today_tickss(self, code: str = None, retry_count: int = 3, pause: float = 0.001) -> DataFrame:
        """
            获取当日分笔明细数据
        Parameters
        ------
            code:string
                      股票代码 e.g. 600848
            retry_count : int, 默认 3
                      如遇网络等问题重复执行的次数
            pause : int, 默认 0
                     重复请求数据过程中暂停的秒数，防止请求间隔时间太短出现的问题
         return
         -------
            DataFrame 当日所有股票交易数据(DataFrame)
                  属性:成交时间、成交价格、价格变动，成交手、成交金额(元)，买卖类型
        """
        df = ts.get_today_tickss(code=code, retry_count=retry_count, pause=pause)
        return df

    '''----------------------以下：股票特色数据----------------------'''

    @retry(max_retry=3, time_interval=2)
    def get_stk_factor(self, ts_code: str = None, trade_date: str = None,
                       start_date: str = None, end_date: str = None) -> DataFrame:
        """
        每日技术面因子数据
        获取股票每日技术面因子数据，用于跟踪股票当前走势情况，数据由Tushare社区自产，覆盖全历史
        ts_code 	str	N	股票代码
        trade_date	str	N	交易日期 （yyyymmdd，下同）
        start_date	str	N	开始日期
        end_date	str	N	结束日期
        _________________________________________
        return
        ts_code	        str	Y	股票代码
        trade_date	    str	Y	交易日期
        close	        float	Y	收盘价
        open	        float	Y	开盘价
        high	        float	Y	最高价
        low	            float	Y	最低价
        pre_close	    float	Y	昨收价
        change	        float	Y	涨跌额
        pct_change	    float	Y	涨跌幅
        vol	            float	Y	成交量 （手）
        amount	        float	Y	成交额 （千元）
        adj_factor	    float	Y	复权因子
        open_hfq	    float	Y	开盘价后复权
        open_qfq	    float	Y	开盘价前复权
        close_hfq	    float	Y	收盘价后复权
        close_qfq	    float	Y	收盘价前复权
        high_hfq	    float	Y	最高价后复权
        high_qfq	    float	Y	最高价前复权
        low_hfq	        float	Y	最低价后复权
        low_qfq	        float	Y	最低价前复权
        pre_close_hfq	float	Y	昨收价后复权
        pre_close_qfq	float	Y	昨收价前复权
        macd_dif	    float	Y	MCAD_DIF (基于前复权价格计算，下同)
        macd_dea	    float	Y	MCAD_DEA
        macd	        float	Y	MCAD
        kdj_k	        float	Y	KDJ_K
        kdj_d	        float	Y	KDJ_D
        kdj_j	        float	Y	KDJ_J
        rsi_6	        float	Y	RSI_6
        rsi_12	        float	Y	RSI_12
        rsi_24	        float	Y	RSI_24
        boll_upper	    float	Y	BOLL_UPPER
        boll_mid	    float	Y	BOLL_MID
        boll_lower	    float	Y	BOLL_LOWER
        cci	            float	Y	CCI
        """
        df = self.pro.stk_factor(ts_code=ts_code, trade_date=trade_date,
                                 start_date=start_date, end_date=end_date)
        return df

    @retry(max_retry=3, time_interval=2)
    def get_sw_daily(self, ts_code: str = None, trade_date: str = None,
                     start_date: str = None, end_date: str = None) -> DataFrame:
        """申万行业数据"""
        df = self.pro.sw_daily(ts_code=ts_code, trade_date=trade_date, start_date=start_date, end_date=end_date)
        return df

    '''----------------------以下：财务数据----------------------'''
    '''
    主要报表类型(report_type)说明
    代码	类型	说明
    1	合并报表	上市公司最新报表（默认）
    2	单季合并	单一季度的合并报表
    3	调整单季合并表	调整后的单季合并报表（如果有）
    4	调整合并报表	本年度公布上年同期的财务报表数据，报告期为上年度
    5	调整前合并报表	数据发生变更，将原数据进行保留，即调整前的原数据
    6	母公司报表	该公司母公司的财务报表数据
    7	母公司单季表	母公司的单季度表
    8	母公司调整单季表	母公司调整后的单季表
    9	母公司调整表	该公司母公司的本年度公布上年同期的财务报表数据
    10	母公司调整前报表	母公司调整之前的原始财务报表数据
    11	母公司调整前合并报表	母公司调整之前合并报表原数据
    12	母公司调整前报表	母公司报表发生变更前保留的原数据
    '''

    @retry(max_retry=3, time_interval=2)
    def get_income(self, ts_code: str = None, ann_date: str = None, f_ann_date: str = None,
                   start_date: str = None, end_date: str = None, period: str = None, report_type: str = None,
                   comp_type: str = None, end_type: str = None) -> DataFrame:
        """
        获取上市公司财务利润表数据
        ts_code	    str	N	股票代码
        ann_date	str	N	公告日期（YYYYMMDD格式，下同）
        f_ann_date	str	N	实际公告日期
        start_date	str	N	公告开始日期
        end_date	str	N	公告结束日期
        period	    str	N	报告期
        report_type	str	N	报告类型
        comp_type	str	N	公司类型（1一般工商业2银行3保险4证券）
        end_type	str	N	报告期编码（1~4表示季度，e.g. 4表示年报
        """
        df = self.pro.income_vip(ts_code=ts_code, ann_date=ann_date, f_ann_date=f_ann_date,
                                 start_date=start_date, end_date=end_date, period=period, report_type=report_type,
                                 comp_type=comp_type, end_type=end_type)
        return df

    @retry(max_retry=3, time_interval=2)
    def get_balancesheet(self, ts_code: str = None, ann_date: str = None, start_date: str = None,
                         end_date: str = None, period: str = None, report_type: str = None,
                         comp_type: str = None, end_type: str = None) -> DataFrame:
        """
        获取上市公司资产负债表
        ts_code	    str	N	股票代码
        ann_date	str	N	公告日期（YYYYMMDD格式，下同）
        start_date	str	N	公告开始日期
        end_date	str	N	公告结束日期
        period	    str	N	报告期
        report_type	str	N	报告类型
        comp_type	str	N	公司类型（1一般工商业2银行3保险4证券）
        end_type	str	N	报告期编码（1~4表示季度，e.g. 4表示年报
        """
        df = self.pro.balancesheet_vip(ts_code=ts_code, ann_date=ann_date, start_date=start_date,
                                       end_date=end_date, period=period, report_type=report_type,
                                       comp_type=comp_type, end_type=end_type)
        return df

    @retry(max_retry=3, time_interval=2)
    def get_cashflow(self):
        """todo 描述：获取上市公司现金流量表"""
        pass

    @retry(max_retry=3, time_interval=2)
    def get_forecast(self):
        """todo 描述：获取业绩预告数据"""
        pass

    @retry(max_retry=3, time_interval=2)
    def get_express(self):
        """todo 描述：获取上市公司业绩快报"""
        pass

    @retry(max_retry=3, time_interval=2)
    def get_dividend(self):
        """todo 描述：分红送股数据"""
        pass

    @retry(max_retry=5, time_interval=2)
    def get_fina_indicator(self, ts_code: str = None, ann_date: str = None, start_date: str = None,
                           end_date: str = None, period: str = None) -> DataFrame:
        """
        获取上市公司财务指标数据 现阶段每次请求最多返回60条记录，可通过设置日期多次请求获取更多数据。
        ts_code	    str	N	TS股票代码,e.g. 600001.SH/000001.SZ
        ann_date	str	N	公告日期
        start_date	str	N	报告期开始日期
        end_date	str	N	报告期结束日期
        period	    str	N	报告期(每个季度最后一天的日期,比如20171231表示年报)
        """
        df = self.pro.fina_indicator_vip(ts_code=ts_code, ann_date=ann_date, start_date=start_date,
                                         end_date=end_date, period=period)
        return df

    @retry(max_retry=3, time_interval=2)
    def get_fina_mainbz(self, ts_code: str = None, period: str = None, start_date: str = None,
                        end_date: str = None, type: str = None) -> DataFrame:
        """
        描述：获得上市公司主营业务构成，分地区和产品两种方式
        ts_code	    str	N	股票代码
        period	    str	N	报告期(每个季度最后一天的日期,比如20171231表示年报)
        type	    str	N	类型：P按产品 D按地区（请输入大写字母P或者D）
        start_date	str	N	报告期开始日期
        end_date	str	N	报告期结束日期
        """
        df = self.pro.fina_mainbz_vip(ts_code=ts_code, period=period, start_date=start_date,
                                      end_date=end_date, type=type)
        return df

    '''----------------------以下：指数相关数据----------------------'''

    @retry(max_retry=3, time_interval=2)
    def get_index_basic(self, ts_code=None, name=None,
                        market=None, publisher=None, category=None) -> DataFrame:
        """"
        描述：获取指数基础信息。
        ts_code	    str	N	指数代码
        name	    str	N	指数简称
        market	    str	N	交易所或服务商(默认SSE)
        publisher	str	N	发布商
        category	str	N	指数类别
        ________________
        return
        ts_code	str	TS代码
        name	str	简称
        fullname	str	指数全称
        market	str	市场
        publisher	str	发布方
        index_type	str	指数风格
        category	str	指数类别
        base_date	str	基期
        base_point	float	基点
        list_date	str	发布日期
        weight_rule	str	加权方式
        desc	str	描述
        exp_date	str	终止日期
        ________________
        市场说明(market)
            市场代码	说明
            MSCI	MSCI指数
            CSI	中证指数
            SSE	上交所指数
            SZSE	深交所指数
            CICC	中金指数
            SW	申万指数
            OTH	其他指数
        指数列表
            主题指数
            规模指数
            策略指数
            风格指数
            综合指数
            成长指数
            价值指数
            有色指数
            化工指数
            能源指数
            其他指数
            外汇指数
            基金指数
            商品指数
            债券指数
            行业指数
            贵金属指数
            农副产品指数
            软商品指数
            油脂油料指数
            非金属建材指数
            煤焦钢矿指数
            谷物指数
        """
        df = self.pro.index_basic(ts_code=ts_code, name=name, market=market,
                                  publisher=publisher, category=category)
        return df

    @retry(max_retry=3, time_interval=2)
    def get_index_dailybasic(self, ts_code: str = None, trade_date: str = None,
                             start_date: str = None, end_date: str = None):
        """
        大盘指数每日指标
        trade_date	str	N	交易日期 （格式：YYYYMMDD，比如20181018，下同）
        ts_code	    str	N	TS代码
        start_date	str	N	开始日期
        end_date	str	N	结束日期
        ________________
        return
        ts_code	str	Y	TS代码
        trade_date	str	Y	交易日期
        total_mv	float	Y	当日总市值（元）
        float_mv	float	Y	当日流通市值（元）
        total_share	float	Y	当日总股本（股）
        float_share	float	Y	当日流通股本（股）
        free_share	float	Y	当日自由流通股本（股）
        turnover_rate	float	Y	换手率
        turnover_rate_f	float	Y	换手率(基于自由流通股本)
        pe	float	Y	市盈率
        pe_ttm	float	Y	市盈率TTM
        pb	float	Y	市净率
        """
        df = self.pro.index_dailybasic(trade_date=trade_date, ts_code=ts_code,
                                       start_date=start_date, end_date=end_date)
        return df

    @retry(max_retry=3, time_interval=2)
    def get_index_daily(self, ts_code, trade_date=None,
                        start_date=None, end_date=None):
        """
        获取指数每日行情，还可以通过bar接口获取
        ts_code	    str	Y	指数代码
        trade_date	str	N	交易日期 （日期格式：YYYYMMDD，下同）
        start_date	str	N	开始日期
        end_date	str	N	结束日期
        _________________________
        return
        ts_code	    str	TS指数代码
        trade_date	str	交易日
        close	    float	收盘点位
        open	    float	开盘点位
        high	    float	最高点位
        low	        float	最低点位
        pre_close	float	昨日收盘点
        change	    float	涨跌点
        pct_chg	    float	涨跌幅（%）
        vol	        float	成交量（手）
        amount	    float	成交额（千元）
        """
        df = self.pro.index_daily(ts_code=ts_code, rade_date=trade_date,
                                  start_date=start_date, end_date=end_date)
        return df


# TODO list
# 公募基金
# 期货
# 现货
# 期权
# 债券
# 外汇
# 港股
# 美股
# 行业经济
# 宏观经济
# 另类数据
# 财富管理
# 数据索引
'''----------------------以上：沪深股票数据----------------------'''
