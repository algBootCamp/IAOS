# -*- coding: utf-8 -*-
__author__ = 'carl'

'''
BaseSecurity : 证券信息实体【基类】
'''


class BaseSecurity(object):

    def __init__(self):
        # 股票代码
        self.__stk_id: str = None
        # 股票名称
        self.__name: str = None
        # 行业
        self.__industry: str = None
        # 地域
        self.__area: str = None
        # 市盈率（动）
        self.__pe_ttm: float = None
        # 市盈率（静）
        self.__pe: float = None
        # 流通股本（亿）
        self.__float_share: float = None
        # 总股本（亿）
        self.__total_share: float = None
        # 总资产（亿）
        self.__total_assets: float = None
        # 流动资产（亿）
        self.__liquid_assets: float = None
        # 固定资产（亿）
        self.__fixed_assets: float = None
        # 公积金
        self.__reserved: float = None
        # 每股公积金
        self.__reserved_pershare: float = None
        # 每股收益
        self.__eps: float = None
        # 每股净资产
        self.__bvps: float = None
        # 市净率
        self.__pb: float = None
        # 上市日期
        self.__list_date: str = None
        # 未分配利润
        self.__undp: float = None
        # 每股未分配利润
        self.__per_undp: float = None
        # 收入同比（ % ）
        self.__rev_yoy: float = None
        # 利润同比（ % ）
        self.__profit_yoy: float = None
        # 毛利率（ % ）
        self.__gpr: float = None
        # 净利润率（ % ）
        self.__npr: float = None
        # 股东人数
        self.__holder_num: int = None

    @property
    def stk_id(self):
        # 股票代码
        return self.__stk_id

    @stk_id.setter
    def stk_id(self, stk_id):
        self.__stk_id = stk_id

    @property
    def name(self):
        # 股票名称
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def industry(self):
        # 行业
        return self.__industry

    @industry.setter
    def industry(self, industry):
        self.__industry = industry

    @property
    def area(self):
        # 地域
        return self.__area

    @area.setter
    def area(self, area):
        self.__area = area

    @property
    def pe_ttm(self):
        # 市盈率（动）
        return self.__pe_ttm

    @pe_ttm.setter
    def pe_ttm(self, pe_ttm):
        self.__pe_ttm = pe_ttm

    @property
    def pe(self):
        # 市盈率（静）
        return self.__pe

    @pe.setter
    def pe(self, pe):
        self.__pe = pe

    @property
    def float_share(self):
        # 流通股本（亿）
        return self.__float_share

    @float_share.setter
    def float_share(self, float_share):
        self.__float_share = float_share

    @property
    def total_share(self):
        # 总股本（亿）
        return self.__total_share

    @total_share.setter
    def total_share(self, total_share):
        self.__total_share = total_share

    @property
    def total_assets(self):
        # 总资产（亿）
        return self.__total_assets

    @total_assets.setter
    def total_assets(self, total_assets):
        self.__total_assets = total_assets

    @property
    def liquid_assets(self):
        # 流动资产（亿）
        return self.__liquid_assets

    @liquid_assets.setter
    def liquid_assets(self, liquid_assets):
        self.__liquid_assets = liquid_assets

    @property
    def fixed_assets(self):
        # 固定资产（亿）
        return self.__fixed_assets

    @fixed_assets.setter
    def fixed_assets(self, fixed_assets):
        self.__fixed_assets = fixed_assets

    @property
    def reserved(self):
        # 公积金
        return self.__reserved

    @reserved.setter
    def reserved(self, reserved):
        self.__reserved = reserved

    @property
    def reserved_pershare(self):
        # 每股公积金
        return self.__reserved_pershare

    @reserved_pershare.setter
    def reserved_pershare(self, reserved_pershare):
        self.__reserved_pershare = reserved_pershare

    @property
    def eps(self):
        # 每股收益
        return self.__eps

    @eps.setter
    def eps(self, eps):
        self.__eps = eps

    @property
    def bvps(self):
        # 每股净资产
        return self.__bvps

    @bvps.setter
    def bvps(self, bvps):
        self.__bvps = bvps

    @property
    def pb(self):
        # 市净率
        return self.__pb

    @pb.setter
    def pb(self, pb):
        self.__pb = pb

    @property
    def list_date(self):
        # 上市日期
        return self.__list_date

    @list_date.setter
    def list_date(self, list_date):
        self.__list_date = list_date

    @property
    def undp(self):
        # 未分配利润
        return self.__undp

    @undp.setter
    def undp(self, undp):
        self.__undp = undp

    @property
    def per_undp(self):
        # 每股未分配利润
        return self.__per_undp

    @per_undp.setter
    def per_undp(self, per_undp):
        self.__per_undp = per_undp

    @property
    def rev_yoy(self):
        # 收入同比（ % ）
        return self.__rev_yoy

    @rev_yoy.setter
    def rev_yoy(self, rev_yoy):
        self.__rev_yoy = rev_yoy

    @property
    def profit_yoy(self):
        # 利润同比（ % ）
        return self.__profit_yoy

    @profit_yoy.setter
    def profit_yoy(self, profit_yoy):
        self.__profit_yoy = profit_yoy

    @property
    def gpr(self):
        # 毛利率（ % ）
        return self.__gpr

    @gpr.setter
    def gpr(self, gpr):
        self.__gpr = gpr

    @property
    def npr(self):
        # 净利润率（ % ）
        return self.__npr

    @npr.setter
    def npr(self, npr):
        self.__npr = npr

    @property
    def holder_num(self):
        # 股东人数
        return self.__holder_num

    @holder_num.setter
    def holder_num(self, holder_num):
        self.__holder_num = holder_num
