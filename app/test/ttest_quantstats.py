import pandas as pd
import quantstats as qs


def cal_daily_return(fund_values: pd.Series):
    """根据资金变动，计算日资产的变化率
    :param fund_values: 每日的总资产
    """
    fund_values = fund_values.sort_index()
    daily_re: pd.Series = (fund_values / fund_values.shift(1)) - 1
    daily_re.iloc[0] = 0
    return daily_re


def cal_rolling_feature(daily_return_series: pd.Series, rf=0.02, record_dict: dict = None):
    """计算各种指标
    :param daily_return_series: 日收益的变化率
    :param rf: 无风险收益，这里定为0.02
    :param record_dict: 指标的结果会追加到这个字典中
    """
    if record_dict is None:
        record_dict = {}
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
