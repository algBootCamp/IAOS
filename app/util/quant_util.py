# -*- coding: utf-8 -*-
__author__ = 'carl'

import pandas as pd
from pandas import DataFrame

from quotation.captures.tsdata_capturer import TuShareDataCapturer


def get_price(ts_code_list, trade_date, asset='E'):
    """
    获取证券列表内收盘价
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
            new_price = tsdatacapture.get_pro_bar(asset=asset, ts_code=ts_codes, start_date=trade_date,
                                                  end_date=trade_date)
            close = pd.concat([close, new_price], axis=0)
    elif len(ts_code_list) == 1:
        close = tsdatacapture.get_pro_bar(asset=asset, ts_code=ts_code_list[0], start_date=trade_date,
                                          end_date=trade_date)
    else:
        ts_codes = symbol.join(ts_code_list)
        # 当且仅当 start_date=end_date  ts_code可传多值
        close = tsdatacapture.get_pro_bar(asset=asset, ts_code=ts_codes, start_date=trade_date,
                                          end_date=trade_date)
    # 实在没办法了 一个一个取 防止多值获取失败
    if close is None or close.empty:
        for ts_code in ts_code_list:
            new_price = tsdatacapture.get_pro_bar(asset=asset, ts_code=ts_code, start_date=trade_date,
                                                  end_date=trade_date)
            close = pd.concat([close, new_price], axis=0)
    close = close[['ts_code', 'close']].sort_values(by='ts_code')
    close.index = close['ts_code']
    return close
