# -*- coding: utf-8 -*-
__author__ = 'carl'

import logging

import numpy as np
from pandas import DataFrame

log = logging.getLogger("log_quantization")
log_err = logging.getLogger("log_err")


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