# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging

import numpy as np
import pandas as pd
import quantstats as qs
from pandas import DataFrame

log = logging.getLogger("log_quantization")
log_err = logging.getLogger("log_err")


# noinspection PyIncorrectDocstring
def get_data_percentile(data: list, v_low=50.0, v_mid=83.83, v_high=94.22) -> tuple:
    """
    获取 data 最大值 最小值  高、中、低分位数
    :param data:
    :return:
    """
    if data is None or len(data) < 1:
        log_err.error("get_data_percentile 参数data异常!")
        raise Exception("get_data_percentile 参数data异常:", data)

    data_max = max(data)
    data_min = min(data)
    valuation_high = np.percentile(data, v_high)
    valuation_mid = np.percentile(data, v_mid)
    valuation_low = np.percentile(data, v_low)
    return data_max, data_min, valuation_low, valuation_mid, valuation_high


def limit_score_range(target_range, org_scorer_col: str, df: DataFrame):
    """打分：将数值限制在target_range内"""
    org_range = df[org_scorer_col].max() - df[org_scorer_col].min()
    df[org_scorer_col] = ((df[org_scorer_col] - df[org_scorer_col].min()) / org_range) * target_range


def cal_daily_return(fund_values: pd.Series) -> pd.Series:
    """
    根据资金变动，计算日资产的变化率
    :param fund_values: 每日的总资产
    """
    fund_values = fund_values.sort_index()
    daily_re: pd.Series = (fund_values / fund_values.shift(1)) - 1
    daily_re.iloc[0] = 0
    return daily_re


def cal_rolling_feature(daily_return_series: pd.Series, rf=0.02):
    """
    计算各种指标
    :param daily_return_series: 日收益的变化率
    :param rf: 无风险收益，这里定为0.02
    """
    record_dict = {}  # 指标的结果会追加到这个字典中
    daily_return_series.index = pd.to_datetime(daily_return_series.index.values)
    feature_df = pd.DataFrame(index=daily_return_series.index)
    feature_df['累积收益率'] = qs.stats.compsum(daily_return_series).values
    feature_df['回撤'] = qs.stats.to_drawdown_series(daily_return_series)
    record_dict.update({"累积收益率": feature_df['累积收益率'].iloc[-1]})
    feature_dict = {
        "复合年增长": qs.stats.cagr(daily_return_series, rf=rf),
        "夏普比率": qs.stats.sharpe(daily_return_series, rf=rf),
        "索蒂诺": qs.stats.sortino(daily_return_series, rf=rf),
        "omega": qs.stats.omega(pd.DataFrame(daily_return_series), rf=rf),
        "最大回撤": qs.stats.max_drawdown(daily_return_series),
        "最大回撤期(天)": int(qs.stats.drawdown_details(feature_df['回撤'])['days'].max()),
        "年波动率": qs.stats.volatility(daily_return_series),
    }
    record_dict.update(feature_dict)
    # 决定保留的小数
    for key, value in record_dict.items():
        if isinstance(value, float):
            record_dict[key] = value.round(3)
    return feature_df, record_dict
