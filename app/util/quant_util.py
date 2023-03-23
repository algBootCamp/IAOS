# -*- coding: utf-8 -*-
__author__ = 'carl'

import pandas as pd
from pandas import DataFrame

from quotation.captures.tsdata_capturer import TuShareDataCapturer


def get_price(ts_code_list, trade_date, asset='E', adj='hfq'):
    """
    获取证券列表内收盘价
    计算区间涨幅、累积涨幅用后复权
    """
    tsdatacapture: TuShareDataCapturer = TuShareDataCapturer()
    symbol = ","
    close = DataFrame()
    # 缓解压力 大于500个 分割
    if len(ts_code_list) > 500:
        f = lambda a: map(lambda b: a[b:b + 300], range(0, len(a), 300))
        part_ports = f(ts_code_list)
        for part_port in part_ports:
            ts_codes = symbol.join(part_port)
            # 当且仅当 start_date=end_date  ts_code可传多值
            new_price = tsdatacapture.get_pro_bar(asset=asset, adj=adj, ts_code=ts_codes, start_date=trade_date,
                                                  end_date=trade_date)
            close = pd.concat([close, new_price], axis=0)
    elif len(ts_code_list) == 1:
        close = tsdatacapture.get_pro_bar(asset=asset, adj=adj, ts_code=ts_code_list[0], start_date=trade_date,
                                          end_date=trade_date)
    else:
        ts_codes = symbol.join(ts_code_list)
        # 当且仅当 start_date=end_date  ts_code可传多值
        close = tsdatacapture.get_pro_bar(asset=asset, adj=adj, ts_code=ts_codes, start_date=trade_date,
                                          end_date=trade_date)
    # 实在没办法了 一个一个取 防止多值获取失败
    if close is None or close.empty:
        for ts_code in ts_code_list:
            new_price = tsdatacapture.get_pro_bar(asset=asset, adj=adj,ts_code=ts_code, start_date=trade_date,
                                                  end_date=trade_date)
            close = pd.concat([close, new_price], axis=0)
    close = close[['ts_code', 'close']].sort_values(by='ts_code')
    close.index = close['ts_code']
    return close


# noinspection DuplicatedCode
def get_period_fl_trade_date(start_date, end_date):
    """
    获取start_date——end_date 之间最初/最后一个交易日
    """
    tsdatacapture: TuShareDataCapturer = TuShareDataCapturer()
    trade_cal = tsdatacapture.get_trade_cal(start_date=start_date, end_date=end_date).sort_values(
        by='cal_date')
    start_date_s = trade_cal.loc[0, "cal_date"]
    end_date_s = trade_cal.loc[len(trade_cal.index) - 1, "cal_date"]
    if int(start_date_s) - int(end_date_s) > 0:
        end_date_s, start_date_s = start_date_s, end_date_s
    return start_date_s, end_date_s
